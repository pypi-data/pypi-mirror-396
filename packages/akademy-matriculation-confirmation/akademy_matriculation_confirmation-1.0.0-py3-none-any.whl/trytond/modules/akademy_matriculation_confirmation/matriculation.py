# This file is part of SAGE Education.   The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.model import fields, ModelView
from trytond.wizard import Button, StateTransition, StateView, Wizard
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Bool, Eval, Not
from trytond.exceptions import UserError

from ..akademy_classe.classe import ClasseStudentDiscipline


class MatriculationCreateWzardStart(metaclass=PoolMeta):
    'Matriculation CreateStart'
    __name__ = 'akademy_matriculation.wizmatriculation.create.start'

    is_candidate = fields.Boolean(
        'Candidato', 
        states={
            'invisible':  Bool(Eval('is_transferred')) | Bool(Eval('is_student'))
        }, depends=['is_transferred', 'is_student'], 
        help="Matrícula para candidato.")
    is_transferred = fields.Boolean(
        'Transferido', 
        states={
            'invisible':  Bool(Eval('is_candidate')) | Bool(Eval('is_student'))
        }, depends=['is_candidate', 'is_student'], 
        help="Matrícula para estudante transferido.")
    is_student = fields.Boolean(
        'Discente', 
        states={
            'invisible':  Bool(Eval('is_candidate')) | Bool(Eval('is_transferred'))
        }, depends=['is_candidate', 'is_transferred'], 
        help="Confirmação de matrícula para estudante.")
    student = fields.Many2One(
        'company.student', 'Discente',
        states={
            'invisible': Not(Bool(Eval('is_student'))), 
            'required': Bool(Eval('is_student'))
        }, help="Caro utilizador será feita a matrícula do discente.")
    classes = fields.Many2One(
        'akademy_classe.classes', 'Turma',
        states={
            'invisible': Not(Bool(Eval('is_student'))), 
            'required': Bool(Eval('is_student'))
        }, help="Informa o nome da turma.")


class MatriculationCreateWzard(metaclass=PoolMeta):
    'Matriculation CreateWzard'
    __name__ = 'akademy_matriculation.wizmatriculation.create'

    start_state = 'start'
    start = StateView(
        'akademy_matriculation.wizmatriculation.create.start', 
        "akademy_matriculation_confirmation.act_matriculation_wizard_from", [
            Button(string=u'Cancelar', state='end', icon='tryton-cancel'),
            Button(string=u'Matricular', state='matriculation', icon='tryton-save')
        ]
    )
    matriculation = StateTransition()

    def transition_matriculation(self):
        if (self.start.is_candidate == True):
            self.student_candidate(self.start.applications.application)
        if (self.start.is_transferred == True):
            self.student_transferred(self.start.transferred)
        if (self.start.is_student == True):
            MatriculationCreateWzard.matriculation_confirmation(self.start.student, self.start.classes)
                    
        return 'end'

    @classmethod
    def matriculation_confirmation(cls, company_student, classes, exception=True):
        student_new_matriculation = []
        ClasseStudent = Pool().get('akademy_classe.classe.student')
        Student_Discipline = Pool().get('akademy_classe.classe.student.discipline')
        CourseYear = Pool().get('akademy_configuration.course.classe')  

        student_has_matriculation = ClasseStudent.search([('student', '=', company_student)])
        classes_course_year = CourseYear.search([
            ('classe', '=', classes.classe), 
            ('course', '=', classes.studyplan.course)
            ], limit=1)
        confirmation = True
        i = 0
        
        student_state = [
                'Aguardando', 'Suspenso(a)', 
                'Anulada', 'Transfêrido(a)', 
                'Reprovado(a)', 'Matrículado(a)'
            ]

        if len(student_has_matriculation) > 0:
            classe_student = student_has_matriculation[len(student_has_matriculation) -1]
            student_course_year = CourseYear.search([
                #('classe', '=', classe_student.classes.classe), 
                ('course', '=', classe_student.classes.studyplan.course)
                ])        
            #verify_year = int(classes_course_year[0].course_year) - int(student_course_year[0].course_year)
            verify_year = int(student_course_year[len(student_course_year)-1].course_year) - int(classes_course_year[0].course_year)
                                               
            for student in student_has_matriculation:

                NoneType = type(None)
                if type(student.student.state) == NoneType:
                    raise UserError("Não foi possível prosseguir com a matrícula. Por favor, preencha os campos não obrigatórios na ficha do discente para continuar com a confirmação da matrícula.")                    
                
                if student.state.name not in student_state:  
                    student_matriculation = ClasseStudent.search([
                        ('student', '=', student.student), 
                        ('classes', '=', classes)
                        ], limit=1)                      
                    confirmation = True
                      
                    if classes == student.classes:
                        raise UserError("O(A) discente "+company_student.party.name+", não pode frequentar a classe "+classes.classe.name+
                                ", na turma "+classes.name+", pois ele já está matriculado nesta turma.")
                    else:
                        if classes > student.classes:                           
                            if len(student_matriculation) == 0:
                                MatriculationCreateWzard.matriculation_student_classe(student, ClasseStudent, company_student, classes, Student_Discipline)                                     
                                #raise UserError("O(A) discente "+company_student.party.name+", não pode frequentar a classe "+classes.classe.name+
                                #        ", na turma "+classes.name+", pois ele já está matriculado nesta turma.")
                            else:        
                                if verify_year == 0:  
                                    if student.state.name in ["Matrículado(a)", "Aprovado(a)"]:
                                        #raise UserError("O discente "+company_student.party.name+", não pode frequentar a classe "+
                                        #                classes.classe.name+", na turma "+classes.name+", pois ele já está matrícula nesta classe e turma.")
                                        pass
                                    if student.state.name == "Reprovado(a)":                                        
                                        pass
                                    
                                elif verify_year == 1:              
                                    if student.state.name == "Aprovado(a)":
                                        if i == 0:
                                            MatriculationCreateWzard.matriculation_student_classe(student, ClasseStudent, company_student, classes, Student_Discipline)                                     
                                            i += 1
                                        else:
                                            pass
                                    if student.state.name == "Reprovado(a)":                                        
                                        confirmation = False
                                                   
                                else:
                                    raise UserError("Não foi possível matricular o discente "+company_student.party.name+
                                                    ", na classe "+classes.classe.name+", pois ele ainda não tem matricula na classe anterior.")
                                                                          
                        else:                            
                            confirmation = False
                else:
                    raise UserError("O discente "+company_student.party.name+", não pode frequentar a classe "+classes.classe.name+
                                    ", na turma "+classes.name+", por favor verifique o estado da matrícula anterior.")

            if confirmation == False:
                raise UserError("O discente "+company_student.party.name+", não pode frequentar a classe "+classes.classe.name+
                                ", pois o mesmo esta reprovado(a) na turma "+company_student.classe.name)

        else:
            course_frist_year = 1
            verify_year = course_frist_year - int(classes_course_year[0].course_year)
            
            if verify_year == 0:
                if student.state.name not in student_state: 
                    MatriculationCreateWzard.matriculation_student_classe(student_new_matriculation, ClasseStudent, company_student, classes, Student_Discipline)                 
            else:
                raise UserError("Não foi possível matricular o discente "+company_student.party.name+
                                ", na classe "+classes.classe.name+", por favor verifique a situação do discente.")

    @classmethod
    def matriculation_student_classe(cls, classe_student, ClasseStudent, company_student, classes, ClasseStudentDiscipline):
        MatriculationState = Pool().get('akademy_configuration.matriculation.state')
        DisciplineModality = Pool().get('akademy_configuration.discipline.modality')
        MatriculationType = Pool().get('akademy_configuration.matriculation.type')

        matriculation_state = MatriculationState.search([
            ('name', '=', "Matrículado(a)")
            ], limit=1)
        matriculation_type = MatriculationType.search([
            ('name', '=', "Transição de classe")
            ], limit=1)
        
        classe_has_student = ClasseStudent.search([
            ('student', '=', company_student), ('classes', '=', classes)
            ])
            
        if len(classe_has_student) == 0:
            MatriculationStudent = ClasseStudent.save_student_matriculation(matriculation_state[0], matriculation_type[0], company_student, classes)        
        
            for studyplan_discipline in classes.studyplan.studyplan_discipline:
                student_matriculation = ClasseStudentDiscipline.search([
                    ('classe_student', '=', MatriculationStudent), 
                    ('studyplan_discipline', '=', studyplan_discipline)
                    ])
                
                if len(student_matriculation) > 0:
                    pass
                else:
                    matriculation_state = MatriculationState.search([
                        ('name', '=', "Matrículado(a)")
                        ], limit=1)
                    discipline_modality = DisciplineModality.search([
                        ('name', '=', "Presencial")
                        ], limit=1)
                    
                    if len(studyplan_discipline.discipline_precedentes) > 0:                    
                        ClasseStudentDiscipline.save_student_discipline(
                            MatriculationStudent, studyplan_discipline, matriculation_state[0], discipline_modality[0])                                        
                    else:      
                        ClasseStudentDiscipline.save_student_discipline(
                            MatriculationStudent, studyplan_discipline, matriculation_state[0], discipline_modality[0])
       

class ChangeMatriculationCreateWizardStart(ModelView):
    "ChangeMatriculation CreateStart"
    __name__ = 'akademy_matriculation_confirmation.wizchangematriculation.create.start'
    
    classe_student = fields.Many2One(
        'akademy_classe.classe.student', 'Discente',
        required=True,
        help="Escolha o discente.")  
    classes = fields.Many2One(
        'akademy_classe.classes', 'Turma',
        required=True,
        help="Escolha a turma onde será feita a mudança.")


class ChangeMatriculationChangeCreateWizard(Wizard):
    "ChangeMatriculation CreateWizard"
    __name__ = 'akademy_matriculation_confirmation.wizchangematriculation.create'

    start_state = 'start'
    start = StateView(
        'akademy_matriculation_confirmation.wizchangematriculation.create.start', 
        "akademy_matriculation_confirmation.act_changematriculation_wizard_from", [
            Button(string=u'Cancelar', state='end', icon='tryton-cancel'),
            Button(string=u'Mudar', state='changematriculation', icon='tryton-save')
        ]
    )
    changematriculation = StateTransition()

    def transition_changematriculation(self):            
        MatriculationState = Pool().get('akademy_configuration.matriculation.state')
        MatriculationType = Pool().get('akademy_configuration.matriculation.type')

        if self.start.classe_student.classes.state == False:     
            if self.start.classe_student.state.name in ["Matrículado(a)"]:
                if self.start.classe_student.classes != self.start.classes and self.start.classe_student.classes.classe == self.start.classes.classe:
                    if self.start.classe_student.classes.studyplan.course == self.start.classes.studyplan.course:
                        
                        matriculation_state = MatriculationState.search([
                            ('name', '=', "Mudança de matrícula")
                            ], limit=1)
                        self.start.classe_student.state = matriculation_state[0]
                        self.start.classe_student.save()

                        for classe_student_discipline in self.start.classe_student.classe_student_discipline:
                            classe_student_discipline.state = matriculation_state[0]
                            classe_student_discipline.save()

                        ClasseStudent = Pool().get('akademy_classe.classe.student')
                        max_student = self.start.classes.max_student + 1
                        
                        if self.start.classes.max_student < max_student:
                            matriculation_state = MatriculationState.search([
                                ('name', '=', "Matrículado(a)")
                                ], limit=1)
                            matriculation_type = MatriculationType.search([
                                ('name', '=', "Mudança de turma")
                                ], limit=1)
                            
                            MatriculationStudent = ClasseStudent(
                                state = matriculation_state[0],
                                type = matriculation_type[0],
                                student = self.start.classe_student.student,
                                classes = self.start.classes,
                            )
                            MatriculationStudent.save()
                                            
                        for studyplan_discipline in self.start.classes.studyplan.studyplan_discipline:
                            DisciplineModality = Pool().get('akademy_configuration.discipline.modality')
                            discipline_modality = DisciplineModality.search([('name', '=', 'Presencial')], limit=1)
                            matriculation_state = MatriculationState.search([('name', '=', 'Matrículado(a)')], limit=1)
                                                    
                            ClasseStudentDiscipline.save_student_discipline(MatriculationStudent, studyplan_discipline, matriculation_state[0], discipline_modality[0])
                            
                    else:            
                        raise UserError("Não foi possível prosseguir com a mudança de turma, porque os cursos são diferentes.")
                else:       
                    raise UserError("Não foi possível prosseguir com a mudança de turma, pois as turmas são iguais ou de classes diferentes.")                                    
            else:      
                raise UserError("Não foi possível prosseguir com a mudança de turma, por favor verifica o estado da matrícula.")
            
        else:
            raise UserError("Não é possível efetuar a matrícula do discente ou candidato, porque a turma já se encontra fechada.")

        return 'end'


