# This file is part of SAGE Education.   The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.pool import Pool
from . import matriculation

def register():
    Pool.register( 
        matriculation.MatriculationCreateWzardStart, 
        matriculation.ChangeMatriculationCreateWizardStart,
        
        module='akademy_matriculation_confirmation', type_='model'
    )
    
    Pool.register(
        matriculation.MatriculationCreateWzard,
        matriculation.ChangeMatriculationChangeCreateWizard,

        module='akademy_matriculation_confirmation', type_='wizard'
    )

       
