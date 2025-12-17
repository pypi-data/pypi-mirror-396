# This file is part of SAGE Education.   The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.model import Check, ModelSQL, ModelView, Unique, fields, sort
from trytond.wizard import Button, StateTransition, StateView, Wizard
from trytond.pyson import Bool, Eval, Not
from trytond.exceptions import UserError
from trytond.pool import Pool
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from ..akademy_classe.classe import ClasseStudentDiscipline
from ..akademy_classe.variables import sel_result


class Candidates(ModelSQL, ModelView):
    'Candidates'
    __name__ = 'akademy_matriculation.candidates'      

    code = fields.Char('Código', size=20,
        help="Código do candidato.")
    date_start = fields.Date('Data de início',
        help="Data de início da formação.")
    date_end = fields.Date('Data de conclusão',
        help="Data de término da formação.") 
    average = fields.Numeric('Média', digits=(2,1), required=True, 
        help=u'Média adquirida no certificado.')
    party = fields.Many2One('party.party', 'Nome', 
        required=True, domain=[('is_person', '=', True)],
        ondelete="RESTRICT", help="Nome do candidato.")   
    institution = fields.Many2One('company.company', 'Instituição', 
        required=True, ondelete="RESTRICT",
        help="Nome da instituição de formação.")       
    area = fields.Many2One('akademy_configuration.area', 'Área', 
        domain=[('academic_level', '=', Eval('academic_level', -1))], 
        depends=['academic_level'], required=True, ondelete="RESTRICT")
    course = fields.Many2One('akademy_configuration.course', 'Curso', 
        domain=[('area', '=', Eval('area', -1))], 
        depends=['area'], required=True, ondelete="RESTRICT")
    academic_level = fields.Many2One('akademy_configuration.academic.level', 
        'Nível acadêmico', required=True, ondelete="RESTRICT") 
    applications = fields.One2Many('akademy_matriculation.applications', 
        'candidate', 'Candidaturas')

    @classmethod
    def __setup__(cls):
        super(Candidates, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [
            ('key', Unique(table, table.party, table.academic_level),
            u'Não foi possível cadastrar o novo candidato, por favor verificar se já existe um candidato, neste nível acadêmico.'),
            ('duration', Check(table, table.date_start < table.date_end),
            u'Não foi possível cadastrar o novo candidato, por favor verifica a data de matrícula e conclusão da formação acadêmico.'),
            ('min_average', Check(table, table.average >= 10),
            u'Não foi possível cadastrar o novo candidato, por favor verificar se a média do certificado é menor que 10.'),
            ('max_average', Check(table, table.average <= 20),
            u'Não foi possível cadastrar o novo candidato, por favor verificar se a média do certificado é maior que 20.')
        ]
        cls._order = [('party', 'ASC')]

    '''
    @classmethod
    def delete(cls, candidates):
        for candidate in candidates:
            for application in candidate.applications:
                if application.state == False:
                    super(Candidates, cls).delete(candidate)
                else:
                    raise UserError("Não foi possível eliminar a candidatura, por favor verificar se a mesma encontra-se bloqueada.")
    '''
            
    def get_rec_name(self, name):
        return self.party.rec_name

    @classmethod
    def search_rec_name(cls, name, clause):
        return [('party.rec_name',) + tuple(clause[1:])]
  

class Applications(ModelSQL, ModelView):
    'Applications'
    __name__ = 'akademy_matriculation.applications' 
            
    state = fields.Boolean('Avaliado')
    description = fields.Text('Descrição')
    reference = fields.Many2One('akademy_configuration.matriculation.reference', 
        'Modalidade', required=True, help="Escolha a modalidade de candidatura.")
    age = fields.Function(
        fields.Integer(
            'Idade'
        ), 'on_change_with_age')
    candidate = fields.Many2One('akademy_matriculation.candidates', 
        'Candidato', required=True, ondelete="RESTRICT")
    phase = fields.Many2One('akademy_configuration.phase', 'Fase', 
        required=True, ondelete="RESTRICT", help="Fase de inscrição da candidatura.")
    lective_year = fields.Many2One('akademy_configuration.lective.year', 
        'Ano letivo', required=True, ondelete="RESTRICT",
        help="Ano letivo que pretende se inscrever.")
    academic_level = fields.Many2One('akademy_configuration.academic.level', 
        'Nível acadêmico', required=True, ondelete="RESTRICT",
        help="Nível acadêmico que pretende se inscrever.")
    area = fields.Many2One('akademy_configuration.area', 'Área', 
        domain=[('academic_level', '=', Eval('academic_level', -1))],
        depends=['academic_level'], required=True, ondelete="RESTRICT")    
    course = fields.Many2One('akademy_configuration.course', 'Curso', 
        domain=[('area','=',Eval('area', -1))],
        depends=['area'], required=True, ondelete="RESTRICT")
    course_classe = fields.Many2One('akademy_configuration.course.classe', 'Classe',
        domain=[('course', '=', Eval('course', 1))],
        depends=['course'], required=True, ondelete="RESTRICT")
    result = fields.One2Many('akademy_matriculation.applications.result', 
        'application', 'Resultado', 
        states={'invisible': Not(Bool(Eval('state')))}, depends=['state'])

    @classmethod
    def __setup__(cls):
        super(Applications, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [
            ('key', Unique(table, table.candidate, table.course, table.phase, table.lective_year),
            u'Não foi possível inscrever o candidato, porque o candidato já esta inscrito neste curso, fase e ano letivo.')
        ]       
        cls._order = [('candidate.party', 'ASC')]     

    '''
    @classmethod
    def delete(cls, applications):
        for application in applications:
            if application.state == False:
                super(Applications, cls).delete(application)
            else:
                raise UserError("Não foi possível eliminar q candidatura, por favor verificar se a mesma encontra-se bloqueada.")
    '''
    
    def get_rec_name(self, name):
        return self.candidate.rec_name

    @classmethod
    def search_rec_name(cls, name, clause):
        return [('candidate.rec_name',) + tuple(clause[1:])]

    @fields.depends('candidate')
    def on_change_with_age(self, name=None):
        if self.candidate.party:
            if self.candidate.party.date_birth:
                now = datetime.now()
                delta = relativedelta(now, self.candidate.party.date_birth)
                years_months_days = delta.years
                
                return years_months_days
        
        return None
            
    @classmethod
    def application_admission_avaliation(cls, ApplicationCriteria, application, ApplicationResult, lective_year):           
        
        if (len(ApplicationCriteria) >= 1):
            for application_criteria in ApplicationCriteria:
                if ((application_criteria.academic_level == application.academic_level)
                and (application_criteria.lective_year == application.lective_year) 
                and (application_criteria.area == application.area) 
                and (application_criteria.course == application.course)
                and (application_criteria.phase >= application.phase)):
                                        
                    if ((application_criteria.average <= application.candidate.average)
                    and (application_criteria.age >= application.age)
                    and (application_criteria.phase >= application.phase)):
                        result_avaliation = 'Admitido'
                        Applications.application_admission(ApplicationResult, application, application_criteria, result_avaliation, lective_year) 
                    else:                   
                        result_avaliation = 'Não admitido'
                        Applications.application_admission(ApplicationResult, application, application_criteria, result_avaliation, lective_year)
        else:
            raise UserError("Não foi possível avaliar a candidatura, por favor,"+
                            " verifica se existe pelo menos um critério de admissão para o curso de "+
                            application.course.name+".")
    
    @classmethod
    def application_admission(cls, ApplicationResult, application, criteria, result_avaliation, lective_year):                 
        total_application_admission = ApplicationResult.search([
            ('application_criteria', '=', criteria), ('result', '=', 'Admitido')
            ]) 
        
        if criteria.student_limit > len(total_application_admission):  
            candidate_has_evaluation = ApplicationResult.search([
                ('phase', '=', criteria.phase), ('application', '=', application),
                ('application_criteria', '=', criteria), ('lective_year', '=', lective_year)
                ])   
            
            if len(candidate_has_evaluation) > 0:
                pass
            else:
                Result = ApplicationResult(
                    result = result_avaliation,
                    phase = criteria.phase,
                    application = application,
                    application_criteria = criteria,
                    lective_year = lective_year
                )
                Result.save() 
                
                Applications.application_change_state(application)
        else:
            raise UserError("Já atingiu o limite máximo de vagas disponíveis.") 

    @classmethod
    def application_change_state(cls, application):        
        application.state = True
        application.save()   
                                        	
    
class ApplicationsResult(ModelSQL, ModelView):
    'Applications Result'
    __name__ = 'akademy_matriculation.applications.result'
        
    result = fields.Selection(selection=sel_result, string=u'Resultado')  
    phase = fields.Many2One('akademy_configuration.phase', 'Fase', required=True)
    application = fields.Many2One('akademy_matriculation.applications', 
        'Candidatura', required=True, ondelete="RESTRICT")
    application_criteria = fields.Many2One('akademy_configuration.application.criteria', 
        'Critério de admissão', required=True, ondelete="RESTRICT")
    lective_year = fields.Many2One('akademy_configuration.lective.year', 
        'Ano letivo', required=True, ondelete="RESTRICT")
     
    @classmethod
    def __setup__(cls):
        super(ApplicationsResult, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [
            ('key', Unique(table, table.application, table.application_criteria),
            u'A candidatura já foi avaliada.')
        ]     
        cls._order = [('application.candidate.party', 'ASC')] 

    '''
    @classmethod
    def delete(cls, applications_result):    
        if len(applications_result) > 0:            
            raise UserError("Não foi possível eliminar o resultado da candidatura.")
    '''
    
    def get_rec_name(self, name):
        return self.application.rec_name

    @classmethod
    def search_rec_name(cls, name, clause):
        return [('application.rec_name',) + tuple(clause[1:])]             


class StudentTransfer(ModelSQL, ModelView):
    'Student - Transfer'
    __name__ = 'akademy_matriculation.student.transfer'

    description = fields.Text('Descrição')
    internal = fields.Boolean(
        'Interna',
        states={ 
            'invisible': Bool(Eval('external')), 
            'required': Not(Bool(Eval('external')))
        }, depends=['external'],
        help="Saindo da instituição.")
    external = fields.Boolean(
        'Externa',
        states={
            'invisible': Bool(Eval('internal')), 
            'required': Not(Bool(Eval('internal')))
        }, depends=['internal'],
        help="Vindo de outra instituição.")
    lective_year = fields.Many2One(
		'akademy_configuration.lective.year', 'Ano letivo', 
        states={ 
            'invisible': Bool(Eval('internal')), 
            'required': Not(Bool(Eval('internal')))
        }, depends=['internal'], ondelete="RESTRICT",
        help="Nome do ano letivo.")
    academic_level = fields.Many2One(
		'akademy_configuration.academic.level', 'Nível acadêmico', 
        states={ 
            'invisible': Bool(Eval('internal')), 
            'required': Not(Bool(Eval('internal')))
        }, depends=['internal'], ondelete="RESTRICT",
        help="Nome da nível acadêmico.")
    area = fields.Many2One(
		'akademy_configuration.area', 'Área', 
        states={ 
            'invisible': Bool(Eval('internal')), 
            'required': Not(Bool(Eval('internal')))
        }, ondelete="RESTRICT",
		domain=[('academic_level', '=', Eval('academic_level', -1))], 
		depends=['academic_level', 'internal'], help="Nome da área.")
    course = fields.Many2One(
		'akademy_configuration.course', 'Curso', 
        states={ 
            'invisible': Bool(Eval('internal')), 
            'required': Not(Bool(Eval('internal')))
        }, ondelete="RESTRICT",
		domain=[('area', '=', Eval('area', -1))],
		depends=['area', 'internal'], help="Nome da curso.")
    course_classe = fields.Many2One(
		'akademy_configuration.course.classe', 'Classe', 
        states={ 
            'invisible': Bool(Eval('internal')), 
            'required': Not(Bool(Eval('internal')))
        }, ondelete="RESTRICT",
        domain=[('course', '=', Eval('course', -1))],
		depends=['course', 'internal'], help="Nome da classe.")
    student = fields.Many2One('company.student', 
        'Discente', required=True, ondelete="RESTRICT")
    student_transfer_discipline = fields.One2Many(
		'akademy_matriculation.student.transfer.discipline', 
        'student_transfer', 'Disciplina')
    
    @classmethod
    def __setup__(cls):
        super(StudentTransfer, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [
            ('key',
            Unique(table, table.lective_year, table.academic_level, table.course, table.course_classe, table.student),
            u'Não foi possível cadastrar a transferência, por favor verifique se o discente já se encontra com uma transferência com estes dados.')
        ]

    @classmethod
    def create(cls, vlist):
        vlist = [x.copy() for x in vlist]
        for values in vlist:
            records = super(StudentTransfer, cls).create(vlist)
            if records:
                if values.get('internal'):                    
                    Student = Pool().get('company.student')
                    StudentTransferDiscipline = Pool().get('akademy_matriculation.student.transfer.discipline')
                    student = Student(values['student'])
                    classe_students = student.classe_student

                    for record in records:
                        for classe_student in classe_students:

                            if len(classe_student.historic_grades) > 0:
                                for historic_grade in classe_student.historic_grades:                                    
                                    student_transfer_discipline = StudentTransferDiscipline(
                                        average = historic_grade.average,
                                        student_transfer = record.id,
                                        discipline = historic_grade.studyplan_discipline.discipline,
                                        course = historic_grade.classes.studyplan.course.id, #record.student.course.id,#
                                        course_classe = historic_grade.classes.studyplan.classe
                                    )
                                    student_transfer_discipline.save()
                            else:    
                                for classe_student_discipline in classe_student.classe_student_discipline:                                                                         
                                    student_transfer_discipline = StudentTransferDiscipline(
                                        average = 0,
                                        student_transfer = record.id,
                                        discipline = classe_student_discipline.studyplan_discipline.discipline,
                                        course = classe_student.classes.studyplan.course.id, #record.student.course.id,#
                                        course_classe = classe_student.classes.studyplan.classe
                                    )
                                    student_transfer_discipline.save()

                return records
            else:
                raise UserError("Não foi possível associar a(s) disciplina(s) ao discente.")

    def get_rec_name(self, name):
        t1 = '%s' % \
            (self.student.rec_name)
        return t1   
    

class StudentTransferDiscipline(ModelSQL, ModelView):
    'Student Tranfer Discipline'
    __name__ = 'akademy_matriculation.student.transfer.discipline'

    course = fields.Function(
		fields.Integer(
			'Curso',
		), 'on_change_with_course')
    average = fields.Numeric('Média', digits=(2,1), required=True) 
    student_transfer = fields.Many2One('akademy_matriculation.student.transfer', 
        'Discente', required=True, ondelete="RESTRICT")
    discipline = fields.Many2One('akademy_configuration.discipline', 
        'Disciplina', required=True, ondelete="RESTRICT")   
    course_classe = fields.Many2One('akademy_configuration.course.classe', 'Classe', 
        required=True, domain=[('course.id', '=', Eval('course', -1))],
        depends=['course'], ondelete="RESTRICT", help="Nome da classe.")
    
    @classmethod
    def __setup__(cls):
        super(StudentTransferDiscipline, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [
            ('uniq_classes',
            Unique(table, table.student_transfer, table.discipline, table.course_classe),
            u'Não foi possível associar está disciplina ao discente, por favor verifique se o mesmo já têm esta disciplina associada.')            
        ]

    def get_rec_name(self, name):
        t1 = '%s' % \
            (self.discipline.rec_name)
        return t1

    @fields.depends('student_transfer')
    def on_change_with_course(self, name=None):  
        if self.student_transfer:
            #if self.student_transfer.external:
            return self.student_transfer.student.course.id
        else:
            return None


class MatriculationCreateWzardStart(ModelView):
    'Matriculation CreateStart'
    __name__ = 'akademy_matriculation.wizmatriculation.create.start'

    is_candidate = fields.Boolean(
        'Candidato', 
        states={
            'invisible':  Bool(Eval('is_transferred')) | Bool(Eval('is_student'))
        }, depends=['is_transferred'], 
        help="Matrícula para candidato.")
    is_transferred = fields.Boolean(
        'Transferido', 
        states={
            'invisible':  Bool(Eval('is_candidate')) | Bool(Eval('is_student'))
        }, depends=['is_candidate'], 
        help="Matrícula para discente transferido.")
    applications = fields.Many2One(
        'akademy_matriculation.applications.result', 'Candidato',
        states={
            'invisible': Not(Bool(Eval('is_candidate'))), 
            'required': Bool(Eval('is_candidate'))
        }, domain=[('result', '=', 'Admitido')], 
        help="Caro utilizador será feita a matrícula do candidato.")
    transferred = fields.Many2One(
        'akademy_matriculation.student.transfer', 'Transferido',
        states={
            'invisible': Not(Bool(Eval('is_transferred'))), 
            'required': Bool(Eval('is_transferred'))
        }, domain=[('external', '=', True)],
        help="Caro utilizador será feita a matrícula do discente transfêrido.")
           
        
class MatriculationCreateWzard(Wizard):
    'Matriculation CreateWzard'
    __name__ = 'akademy_matriculation.wizmatriculation.create'

    start_state = 'start'
    start = StateView(
        'akademy_matriculation.wizmatriculation.create.start', 
        "akademy_matriculation.act_matriculation_wizard_from", [
            Button(string=u'Cancelar', state='end', icon='tryton-cancel'),
            Button(string=u'Matricular', state='matriculation', icon='tryton-save')
        ]
    )
    matriculation = StateTransition()

    def transition_matriculation(self):       
        if (self.start.is_candidate == True):
            MatriculationCreateWzard.student_candidate(self.start.applications.application)
        if (self.start.is_transferred == True):
            MatriculationCreateWzard.student_transferred(self.start.transferred)
                    
        return 'end'
    
    @classmethod
    def student_candidate(cls, application):
        NewStudent = Pool().get('company.student')        
        MatriculationState = Pool().get('akademy_configuration.matriculation.state')
        
        if len(application.candidate.party.student) > 0:
            MatriculationCreateWzard.candidate_matriculation(application, application.candidate.party.student[0], 'Candidato(a)')          
        else:
            student_matriculatio = NewStudent.search([
                ('party','=',application.candidate.party),
                ('academic_level','=',application.academic_level),
                ('area','=',application.area),
                ('course','=',application.course)
                ])
            
            if len(student_matriculatio) <= 0:
                state = MatriculationState.search([('name', '=', 'Matrículado(a)')], limit=1),
                matriculation_state = state[0]                
                Matriculation = NewStudent(
                    state = matriculation_state[0],
                    course = application.course,
                    area = studapplicationent.area,
                    academic_level = application.academic_level,
                    start_date = date.today(),
                    party = application.candidate.party,
                )
                Matriculation.save()

                MatriculationCreateWzard.candidate_matriculation(application, Matriculation, 'Candidato(a)')        
        
    @classmethod
    def candidate_matriculation(cls, application, matriculation, type):
        ClasseStudent = Pool().get('akademy_classe.classe.student')
        Classes = Pool().get('akademy_classe.classes')
        MatriculationState = Pool().get('akademy_configuration.matriculation.state')
        MatriculationType = Pool().get('akademy_configuration.matriculation.type')        
        
        if len(application.area.studyplan) <= 0:
            raise UserError("Infelizmente, não é possível matricular o discente, pois a área ainda não possui planos de estudos.")

        get_classes = Classes.search([
            ('lective_year', '=', application.lective_year),
            ('classe', '=', application.course_classe.classe),
            ('studyplan.course', '=', application.course),
            ])

        if len(get_classes) > 0:
            if get_classes[0].state == False:
                if (get_classes[0].max_student != len(get_classes[0].classe_student)):
                    matriculation_state = MatriculationState.search([('name', '=', 'Matrículado(a)')], limit=1)
                    matriculation_type = MatriculationType.search([('name', '=', type)], limit=1)                                                
                    MatriculationStudent = MatriculationCreateWzard.create_student_matriculation(
                        application, ClasseStudent, matriculation_state[0], matriculation_type[0], 
                        matriculation, get_classes[0], get_classes[0].classe, 0
                    )
                    
                    if len(application.area.studyplan[0].studyplan_discipline) > 0:
                        MatriculationCreateWzard.discipline_matriculation(MatriculationStudent, get_classes[0].studyplan.studyplan_discipline) 

                else:
                    raise UserError("Infelizmente não é possível matricular o discente, porque ja excedeu o limite de vagas disponíveis.")
            else:
                raise UserError("Não é possível efetuar a matrícula do discente ou candidato, porque a turma já se encontra fechada.")
        else:
            raise UserError("Não foi possível efetuar a matrícula do discente ou candidato, porque ainda não existe uma turma criada.")      
    
    @classmethod
    def create_student_matriculation(cls, classe_student, ClasseStudent, matriculation_state, matriculation_type, student, classes, classe, update):   
        if matriculation_state:
            student_matriculation = ClasseStudent.save_student_matriculation(matriculation_state, matriculation_type, student, classes)
            MatriculationCreateWzard.update_student_company_state(student, classe, matriculation_state)        

        if update:                
            MatriculationCreateWzard.update_student_state(classe_student)

        return student_matriculation

    @classmethod
    def update_student_company_state(cls, company_student, classe, matriculation_state): 
        company_student.state = matriculation_state
        company_student.classe = classe
        company_student.save()

    @classmethod
    def update_student_state(cls, classe_student):
        MatriculationState = Pool().get('akademy_configuration.matriculation.state')
        classe_student.state = MatriculationState.search([('name', '=', "Aprovado(a)")])
        classe_student.save()

    @classmethod
    def discipline_matriculation(cls, student, studyplan_discipline):
        StudentClasseDiscipline = Pool().get('akademy_classe.classe.student.discipline')        
        
        if len(studyplan_discipline) > 0:
            for discipline in studyplan_discipline:
                student_matriculation = StudentClasseDiscipline.search([
                    ('classe_student', '=', student), 
                    ('studyplan_discipline', '=', discipline)
                    ])                
                if len(student_matriculation) <= 0:                                                           
                    MatriculationState = Pool().get('akademy_configuration.matriculation.state')
                    DisciplineModality = Pool().get('akademy_configuration.discipline.modality')
                    discipline_modality = DisciplineModality.search([('name', '=', 'Presencial')], limit=1)
                    matriculation_state = MatriculationState.search([('name', '=', 'Matrículado(a)')], limit=1)                     

                    ClasseStudentDiscipline.save_student_discipline(student, discipline, matriculation_state[0], discipline_modality[0])                    
        else:
            raise UserError("Não é possível associar disciplinas ao discente, pois ele não reprovou em nenhuma das disciplinas frequentadas na turma "+
                student[0].classes.name+" durante o ano letivo de "+student[0].classes.lective_year.name+
                " e já está matriculado nessas disciplinas..")
    
    @classmethod
    def student_transferred(cls, student):  
        Studyplan = Pool().get('akademy_configuration.studyplan')        
        get_studyplan = Studyplan.search([
            ('area', '=', student.area),
            ('course', '=', student.course)
            ])
                
        #EQUIVALENCY PROCESS
        for studyplan in get_studyplan:
            discipline_required = []
            student_discipline_possitive = []
            get_student_transferred_discipline = []
            discipline_positive = []

            for studyplan_discipline in studyplan.studyplan_discipline:   
                if len(student.student_transfer_discipline) > 0: 
                    for student_transfer_discipline in student.student_transfer_discipline:
                            if (student_transfer_discipline.discipline ==  studyplan_discipline.discipline):
                                if (studyplan_discipline.average > student_transfer_discipline.average):                                
                                    get_student_transferred_discipline.append(studyplan_discipline)                                    
                                else:                                   
                                    student_discipline_possitive.append(student_transfer_discipline)                                    
                                    discipline_positive.append(studyplan_discipline)                                    
                else:
                    get_student_transferred_discipline.append(studyplan_discipline)

                #and studyplan_discipline.state.required == True:
                if studyplan_discipline.state.name == "Obrigatório":
                    discipline_required.append(studyplan_discipline)
                    
            if len(discipline_required) == len(student_discipline_possitive):                            
                pass
            else:
                MatriculationCreateWzard.student_transfer_classe(studyplan, get_student_transferred_discipline, discipline_positive, student_discipline_possitive, student)

    @classmethod
    def student_transfer_classe(cls, studyplan, get_student_transferred_discipline, discipline_positive, student_discipline_possitive, student):
        Classes = Pool().get('akademy_classe.classes')
        ClasseStudent = Pool().get('akademy_classe.classe.student')
        Student = Pool().get('company.student')
        MatriculationState = Pool().get('akademy_configuration.matriculation.state')
        MatriculationType = Pool().get('akademy_configuration.matriculation.type')

        for studyplan_discipline in studyplan.studyplan_discipline:
            if studyplan_discipline not in discipline_positive and studyplan_discipline not in get_student_transferred_discipline:                        
                get_student_transferred_discipline.append(studyplan_discipline)
        
        if len(student_discipline_possitive) == 0:
            classe_matriculation = studyplan_discipline.studyplan.classe.classe
        else:
            classe_matriculation = student_discipline_possitive[0].course_classe.classe
        
        get_classes = Classes.search([
            ('lective_year', '=', student.lective_year),
            ('classe', '=', classe_matriculation),
            ('studyplan', '=', studyplan)
            ])

        if get_classes[0].state == False: 
            if len(student.student.classe_student) > 0:
                raise UserError("Infelizmente não é possível matricular o discente, porque o discente já está matriculado.")                    
            else:
                if len(get_classes) > 0:                        
                    get_class_student = ClasseStudent.search(
                        [
                            ('student', '=', student.student),
                            ('classes', '=', get_classes[0])
                        ]
                    ) 
                    
                    if len(get_class_student) > 0:
                        raise UserError("O discente "+student.student.party.name+" já existe na instituição, por favor verifique a matrícula na "+get_class_student[0].classes.name+".")                        
                    else:
                        if (get_classes[0].max_student != len(get_classes[0].classe_student)):
                            matriculation_state = MatriculationState.search([('name', '=', 'Matrículado(a)')], limit=1)
                            matriculation_type = MatriculationType.search([('name', '=', 'Transfêrido(a)')], limit=1)

                            MatriculationCreateWzard.create_student_matriculation(student, ClasseStudent, matriculation_state[0], matriculation_type[0], student.student, get_classes[0], get_classes[0].classe, 0)                                                        
                            student_matriculation = Student.search([
                                ('party','=',student.student.party),
                                ('academic_level','=',student.student.academic_level),
                                ('area','=',student.student.area),
                                ('course','=',student.student.course)
                                ])
                            
                            if len(student_matriculation) > 0:
                                state = MatriculationState.search([('name', '=', 'Matrículado(a)')], limit=1)
                                student_matriculation[0].state = state[0]
                                student_matriculation[0].save()
                                                        
                            MatriculationCreateWzard.student_transferred_discipline(student.student.classe_student, get_student_transferred_discipline, get_classes[0].studyplan)
                        else:
                            raise UserError("Infelizmente não é possível matricular o discente, porque ja excedeu o limite de vagas disponíveis.")
                else:
                    raise UserError("Infelizmente não é possível matricular o discente, porque não foi encontrado um encontrado uma turma disponivel.")           
    
        else:
            raise UserError("Não é possível efetuar a matrícula do discente ou candidato, porque a turma já se encontra fechada.")
    
    @classmethod
    def student_transferred_discipline(cls, student, discipline_negative, studyplan):        
        if len(studyplan.studyplan_discipline) > 0:
            if len(discipline_negative) > 0:
                MatriculationCreateWzard.association_discipline(student, discipline_negative)
            else:
                raise UserError("Infelizmente não é possível associar disciplinas ao discente, porque não há negativas.")        
        else:
            raise UserError("Infelizmente não é possível associar disciplinas ao discente, porque não foi encontrado um plano de estudo compatível com o seu percurso acadêmico.")

    @classmethod
    def association_discipline(cls, student, studyplan_discipline):
        StudentClasseDiscipline = Pool().get('akademy_classe.classe.student.discipline')                 
        if len(studyplan_discipline) > 0:
            for discipline in studyplan_discipline:                
                student_matriculation = StudentClasseDiscipline.search([
                    ('classe_student', '=', student[0]), 
                    ('studyplan_discipline', '=', discipline)
                    ])                
                if len(student_matriculation) <= 0:            
                    MatriculationState = Pool().get('akademy_configuration.matriculation.state')
                    DisciplineModality = Pool().get('akademy_configuration.discipline.modality')
                    discipline_modality = DisciplineModality.search([('name', '=', 'Presencial')], limit=1)
                    matriculation_state = MatriculationState.search([('name', '=', 'Matrículado(a)')], limit=1)                     
           
                    ClasseStudentDiscipline.save_student_discipline(student[0], discipline, matriculation_state[0], discipline_modality[0])
                    
        else:
            raise UserError("Não é possível associar disciplinas ao discente, pois ele não reprovou em nenhuma disciplina na turma "+
                student[0].classes.name+" durante o ano letivo de "+student[0].classes.lective_year.name+
                " e já está matriculado nessas disciplinas.")
 

class AssociationDisciplineCreateWzardStart(ModelView):
    'AssociationDiscipline CreateStart'
    __name__ = 'akademy_matriculation.wizassociatiodiscipline.create.start'

    classes = fields.Many2One(
        'akademy_classe.classes', 'Turma', required=True,
        help="Caro utilizador será feita uma associação entre os discentes desta turma e as displinas existentes no plano de estudo."
    )


class AssociationDisciplineCreateWzard(Wizard):
    'AssociationDiscipline CreateWzard'
    __name__ = 'akademy_matriculation.wizassociatiodiscipline.create'

    start_state = 'start'
    start = StateView(
        'akademy_matriculation.wizassociatiodiscipline.create.start', 
        "akademy_matriculation.act_associationdiscipline_wizard_from", [
            Button(string=u'Cancelar', state='end', icon='tryton-cancel'),
            Button(string=u'Associar', state='association', icon='tryton-save')
        ]
    )
    association = StateTransition()

    def transition_association(self):
        StudentDiscipline = Pool().get('akademy_classe.classe.student.discipline')
        DisciplineModality = Pool().get('akademy_configuration.discipline.modality')

        state_student = ['Aguardando', 'Suspenso(a)', 'Anulada', 'Transfêrido(a)', 'Reprovado(a)']
        list_matriculation = 0

        if self.start.classes.state == False:
            for classe_student in self.start.classes.classe_student:
                if classe_student.state.name not in state_student:
                    for studyplan_discipline in self.start.classes.studyplan.studyplan_discipline:
                        matriculaton_discipline = StudentDiscipline.search(
                            [('classe_student', '=', classe_student), ('studyplan_discipline', '=', studyplan_discipline)]
                        )
                        
                        if (len(matriculaton_discipline) < 1):
                            list_matriculation = 1
                            discipline_modality = DisciplineModality.search([('name', '=', "Presencial")], limit=1)

                            matriculaton = StudentDiscipline(
                                classe_student = classe_student,
                                studyplan_discipline = studyplan_discipline,
                                state = classe_student.state,
                                modality = discipline_modality[0]
                            )
                            matriculaton.save()

            if list_matriculation == 0:
                raise UserError("Não foi possível associar disciplinas aos discentes desta turma, por favor verificar se a turma tem discentes ou se todas as disciplinas já foram associadas.")		

        else:
            raise UserError("Não é possível efetuar a matrícula do discente ou candidato, porque a turma já se encontra fechada.")
                    
        return 'end'  


class ApplicationAvaliationCreateWzardStart(ModelView):
    "ApplicationAvaliation CreateStart"
    __name__ = 'akademy_matriculation.wizapplication_avaliation.create.start'

    applications_criteria = fields.Many2One(
        'akademy_configuration.application.criteria', 'Critério de admissão',       
        help="Caro utilizador escolha o critério de admissão.")


class ApplicationAvaliationCreateWzard(Wizard):
    "ApplicationAvaliation Create"
    __name__ = 'akademy_matriculation.wizapplication_avaliation.create'

    start_state = 'start'
    start = StateView(
        'akademy_matriculation.wizapplication_avaliation.create.start',
        "akademy_matriculation.act_application_avaliation_wizard_from", [
            Button(string=u'Cancelar', state='end', icon='tryton-cancel'),
            Button(string=u'Avaliar', state='application_avaliation', icon='tryton-save')
        ]
    )
    application_avaliation = StateTransition()

    def transition_application_avaliation(self):
        Criteria = Pool().get('akademy_configuration.application.criteria')
        ApplicationResult = Pool().get('akademy_matriculation.applications.result') 
        Applications = Pool().get('akademy_matriculation.applications') 
        
        candidate_application = Applications.search([
            ('phase', '=', self.start.applications_criteria.phase),
            ('lective_year', '=', self.start.applications_criteria.lective_year),
            ('academic_level', '=', self.start.applications_criteria.academic_level),
            ('area', '=', self.start.applications_criteria.area),
            ('course', '=', self.start.applications_criteria.course)
            ])
        
        if self.start.applications_criteria.phase.start <= date.today() <= self.start.applications_criteria.phase.end:
            if len(candidate_application) >= 1:
                #application_sorted = []
                #for value in candidate_application:
                #    application_sorted.append(value)                

                #application_sort = sorted(application_sorted, key=lambda application_sort: [application_sort.age, application_sort.candidate.average])           

                order = [('age', 'ASC'), ('candidate.average', 'ASC')]
                application_sort = sort(candidate_application, order)
                
                for element in application_sort:                
                    phase_admission = element.phase
                    ApplicationCriteria = Criteria.search([('course', '=', element.course), ('phase', '=', phase_admission)])                  
                    
                    if len(ApplicationCriteria) > 0:
                        Result = ApplicationResult.search([
                            ('result', '=', 'Admitido'), 
                            ('application_criteria', '=', ApplicationCriteria[0]),
                            ('lective_year', '=', element.lective_year)
                            ]) 
                    
                        limit = len(Result)
                        if len(ApplicationCriteria) >= 1:
                            if ApplicationCriteria[0].student_limit >= limit: 
                                if len(element.result) <= 1:
                                    Applications.application_admission_avaliation(ApplicationCriteria, element, ApplicationResult, element.lective_year)
                                else:
                                    raise UserError("Não foi possível avaliar a candidatura do candidato(a) "+element.candidate.party.name+
                                                    ", por favor verificar se já existe uma candidatura avaliada para o mesmo.")
                            else:
                                raise UserError("Não foi possível avaliar a candidatura, porque já excedeu o limit estabelecido pela instituição.")
                        else:
                            raise UserError("Não foi possível avaliar a candidatura. Por favor, verifique se existe pelo menos um critério de admissão na fase "+
                                            element.phase.name+", para o curso de "+element.course.name+".\nOu se o candidato(a) "+element.candidate.party.name+
                                            ", já possui uma candidatura para neste curso e neste ano letivo.")
                    else:
                        raise UserError("Não foi possível avaliar a candidatura, porque não foi possível encontrar um critério de admissão,"+
                                        " para a fase "+self.start.applications_criteria.phase.name)
        else:
            raise UserError("Não foi possível avaliar a candidatura, porque já se encontra fora do período de avaliação de candidatura da fase "+
                            self.start.applications_criteria.phase.name)
    
        return 'end'
        
