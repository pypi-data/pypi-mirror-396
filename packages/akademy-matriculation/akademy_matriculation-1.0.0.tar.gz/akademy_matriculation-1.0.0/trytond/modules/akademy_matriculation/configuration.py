# This file is part of SAGE Education.   The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.model import ModelView, ModelSQL, fields, Unique, Check
from trytond.pool import PoolMeta
from trytond.pyson import Eval
from trytond.exceptions import UserError
from datetime import date


class MatriculationReference(ModelSQL, ModelView):
    "Matriculation Reference"
    __name__ = 'akademy_configuration.matriculation.reference'

    name = fields.Char('Nome', required=True,
        help="Nome da referência de candidatura.\nEx: Particular, Bolseiro")
    applications = fields.One2Many('akademy_matriculation.applications', 
        'reference', 'Modalidade de candidatura')

    @classmethod
    def __setup__(cls):
        super(MatriculationReference, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [
            ('name', Unique(table, table.name),
            u'Não foi possível cadastrar a nova referência de candidatura, por favor verificar se o nome inserido já existe.')
        ]


class Phase(ModelSQL, ModelView):
    'Phase'
    __name__ = 'akademy_configuration.phase'

    code = fields.Char('Código', size=20,
        help="Código do fase.")
    name = fields.Char('Nome', required=True, 
        help="Nome da fase de admissão.")
    start = fields.Date('Início', required=True,          
        help="Data de início do ano letivo.")
    end = fields.Date('Término', required=True, 
        help="Data de término do ano letivo.")
    lective_year = fields.Many2One('akademy_configuration.lective.year', 
        'Ano letivo', required=True, ondelete="RESTRICT")
    application_criteria = fields.One2Many('akademy_configuration.application.criteria', 
        'phase', 'Critério de admissão')

    @classmethod
    def __setup__(cls):
        super(Phase, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [
            ('name', Unique(table, table.name, table.code),
            u'Não foi possível cadastrar a nova fase de admissão, por favor verificar se o nome ou código inserido já existe.'),
            ('start_date', Check(table, table.start < table.end),
            u'Não foi possível cadastrar o novo ano letivo, por favor verificar se a data de início é menor que a data de término.')
        ]
    
    @classmethod
    def default_start(cls):
        return date.today() 


class LectiveYear(metaclass=PoolMeta):
    'Lective Year'
    __name__ ='akademy_configuration.lective.year'

    phase = fields.One2Many('akademy_configuration.phase', 
        'lective_year', 'Fase de admissão')
    application_criteria = fields.One2Many('akademy_configuration.application.criteria', 
        'lective_year', 'Critério de admissão')


class AcademicLevel(metaclass=PoolMeta):
    'Academic Level'
    __name__ ='akademy_configuration.academic.level'
    
    application_criteria = fields.One2Many('akademy_configuration.application.criteria', 
        'academic_level', 'Critério de admissão')  


class Area(metaclass=PoolMeta):
    'Area'
    __name__ ='akademy_configuration.area'
    
    application_criteria = fields.One2Many('akademy_configuration.application.criteria', 
        'area', 'Critério de admissão')     


class Course(metaclass=PoolMeta):
    'Course'
    __name__ ='akademy_configuration.course'
        
    application_criteria = fields.One2Many('akademy_configuration.application.criteria', 
        'course', 'Critério de admissão')


class CourseClasse(metaclass=PoolMeta):
    'Course Classe'
    __name__ ='akademy_configuration.course.classe'
          
    application_criteria = fields.One2Many('akademy_configuration.application.criteria', 
        'course_classe', 'Critérios de admissão')


class ApplicationCriteria(ModelSQL, ModelView):
    'Application Criteria'
    __name__ = 'akademy_configuration.application.criteria'

    code = fields.Char('Código', size=20,
        help="Código do critério de admissão.")
    name = fields.Char('Nome', required=True,
        help="Nome do critéio de admissão.")
    description = fields.Text('Descrição')
    age = fields.Integer('Idade', required=True, 
        help=u'Informe a idade máxima para admissão.')
    average = fields.Numeric('Média', digits=(2,1), 
        required=True, help="Informe a média mínima para admissão.")
    student_limit = fields.Integer('Total de vagas', required=True, 
        help="Informe o limite de discentes por admitir.")
    lective_year = fields.Many2One('akademy_configuration.lective.year', 
        'Ano letivo', required=True, ondelete="RESTRICT")
    academic_level = fields.Many2One('akademy_configuration.academic.level', 
        'Nível académico', required=True, ondelete="RESTRICT")
    area = fields.Many2One('akademy_configuration.area', 'Área', 
        domain=[('academic_level', '=', Eval('academic_level', -1))],
        depends=['academic_level'], required=True, ondelete="RESTRICT")    
    course = fields.Many2One('akademy_configuration.course', 'Curso', 
        domain=[('area', '=', Eval('area', -1))],
        depends=['area'], required=True, ondelete="RESTRICT")
    course_classe = fields.Many2One(
        'akademy_configuration.course.classe', 'Classe', 
        required=True, domain=[('course', '=', Eval('course', -1))],
        depends=['course'], ondelete="RESTRICT", help="Nome da classe.")
    phase = fields.Many2One('akademy_configuration.phase', 
        'Fase', required=True, ondelete="RESTRICT")
    application_result = fields.One2Many('akademy_matriculation.applications.result', 
        'application_criteria', 'Resultado das candidaturas')

    @classmethod
    def __setup__(cls):
        super(ApplicationCriteria, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [
            ('name', Unique(table, table.name, table.course, table.lective_year, table.phase),
            u'Não foi possível cadastrar o novo critério de admissão, por favor verificar se já existe um critério de admissão, para  está fase de admissão.'),
            #('age', Check(table, table.age >= 5),
            #u'Não foi possível cadastrar o novo critério de admissão, por favor verificar se a idade inserida.'),
            ('min_average', Check(table, table.average >= 10),
            u'Não foi possível cadastrar o novo critério de admissão, por favor verificar se a média esta abaixo de 10 valores.'),
            ('max_average', Check(table, table.average <= 20),
            u'Não foi possível cadastrar o novo critério de admissão, por favor verificar se a média esta acima de 20 valores.'),
            ('student', Check(table, table.student_limit > 0),
            u'Não foi possível cadastrar o novo critério de admissão, por favor verifica o limite de vagas disponivés.'),
        ]

    @classmethod
    def delete(cls, application_criterias):
        for application_criteria in application_criterias:        
            if len(application_criteria.application_result) < 1:
                super(ApplicationCriteria, cls).delete(application_criteria)
            else:
                raise UserError("Não foi possível eliminar o critério de admissão, porque já existe uma candidatura associada ao mesmo.")
        
    @classmethod
    def default_student_limit(cls):
        return 0

