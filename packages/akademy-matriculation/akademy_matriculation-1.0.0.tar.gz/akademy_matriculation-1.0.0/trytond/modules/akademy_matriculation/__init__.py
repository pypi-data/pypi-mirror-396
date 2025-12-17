# This file is part of SAGE Education.   The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.pool import Pool
from . import matriculation
from . import configuration
from . import party
from . import report

def register():
    Pool.register( 
        configuration.MatriculationReference,
        configuration.ApplicationCriteria,
        configuration.LectiveYear,
        configuration.Area,
        configuration.Course,
        configuration.CourseClasse,
        configuration.AcademicLevel,
        configuration.Phase,
        matriculation.Candidates, 
        matriculation.Applications,
        matriculation.ApplicationsResult,
        matriculation.StudentTransfer,
        matriculation.StudentTransferDiscipline,
        matriculation.MatriculationCreateWzardStart, 
        matriculation.AssociationDisciplineCreateWzardStart,
        matriculation.ApplicationAvaliationCreateWzardStart,
        party.Party,

        module='akademy_matriculation', type_='model'
    )

    Pool.register(
        matriculation.MatriculationCreateWzard,
        matriculation.AssociationDisciplineCreateWzard,
        matriculation.ApplicationAvaliationCreateWzard,

        module='akademy_matriculation', type_='wizard'
    )

    Pool.register(
        report.ApplicationCriteriaReport,
        report.CandidatesReport,
        report.ApplicationResultReport,
        report.StudentTransferReport,
        report.StudentTransferInternalReport,
        report.EquivalenceDisciplineReport,

        module='akademy_matriculation', type_='report'               
    )

