from fpdf import FPDF
from ToDo_tasks.models import TaskModel, AttachmentFilesModel
import os


def pdf_gen(pk):
    task_from_model = TaskModel.objects.get(id=pk)
    ovz = task_from_model.department_number.command_number
    opz = task_from_model.incoming_dep.command_number
    obj = task_from_model.task_object
    order = task_from_model.task_order
    building = task_from_model.task_building
    contract = task_from_model.task_contract.contract_name
    contract_stage = task_from_model.task_stage.stage_name
    kind = task_from_model.task_type_work
    mark = 'ТХ',  # Марка документации
    task = task_from_model.task_number
    content = task_from_model.text_task
    cpe = task_from_model.cpe_sign_user
    if cpe:
        cpe_job_title = task_from_model.cpe_sign_user.job_title
    else:
        cpe_job_title = "ГИП"
    cpe_date = task_from_model.cpe_sign_date
    ruk1 = task_from_model.first_sign_user
    ruk1_job_title = task_from_model.first_sign_user.job_title
    ruk1_date = task_from_model.first_sign_date
    ruk2 = task_from_model.second_sign_user
    ruk2_job_title = task_from_model.second_sign_user.job_title
    ruk2_date = task_from_model.second_sign_date
    isp = task_from_model.author
    isp_job_title = task_from_model.author.job_title
    isp_date = task_from_model.cpe_sign_date
    isp_phone = task_from_model.author.user_phone
    getter = task_from_model.incoming_employee
    if getter:
        getter_job_title = task_from_model.incoming_employee.job_title
    else:
        getter_job_title = "Не определен"
    getter_date = task_from_model.incoming_date
    cpe_comment = task_from_model.cpe_comment

    cpe_mark0 = task_from_model.cpe_sign_status
    ruk1_mark0 = task_from_model.first_sign_status
    ruk2_mark0 = task_from_model.second_sign_status
    isp_mark0 = True
    getter_mark0 = task_from_model.incoming_status


    files_in_db = AttachmentFilesModel.objects.get_queryset().filter(task_id=pk)
    for file in files_in_db:
        print(file)

    structure = 'План на отм.0.000.dwg\nСхема.pdf'



    default_date = ''  # как request.post возвращает пустую дату

    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.add_font('times', '', '../monitoring_tasks/ToDo_tasks/pdf_making/times.ttf', uni=True)
    pdf.set_font('times', '', 14)
    pdf.add_font('timesbd', '', '../monitoring_tasks/ToDo_tasks/pdf_making/timesbd.ttf', uni=True)
    pdf.image('../monitoring_tasks/ToDo_tasks/pdf_making/image/w.jpg', x=10, y=10, w=2.76*30, h=30)

    pdf.x = 10
    pdf.y = 45
    pdf.set_font('timesbd', '', 13)
    pdf.multi_cell(50, 7, txt="Отдел, выдающий задание:", align="L")
    pdf.set_font('times', '', 13)
    pdf.cell(60, 7, txt=f"{ovz}", ln=1, align="C", border='B')
    pdf.set_font('timesbd', '', 13)
    pdf.multi_cell(50, 7, txt="Отдел, принимающий задание:", align="L")
    pdf.set_font('times', '', 13)
    pdf.cell(60, 7, txt=f"{opz}", ln=1, align="C", border='B')
    downO = pdf.y

    pdf.x = 80
    pdf.y = 10
    pdf.set_font('timesbd', '', 13)
    pdf.multi_cell(50, 7, txt='Наименование объекта\nкапитального строительства:', align='L')
    down1 = pdf.y
    pdf.x = 130
    pdf.y = 10
    pdf.set_font('times', '', 13)
    pdf.multi_cell(70, 7, txt=f'{obj}', align='L')
    down1 = max(down1, pdf.y)
    pdf.line(130, down1, 200, down1)

    pdf.x = 80
    pdf.y = down1
    pdf.set_font('timesbd', '', 13)
    pdf.multi_cell(50, 7, txt='Номер заказа:', align='L')
    down2 = pdf.y
    pdf.x = 130
    pdf.y = down1
    pdf.set_font('times', '', 13)
    pdf.multi_cell(70, 7, txt=f'{order}', align='L')
    down2 = max(down2, pdf.y)
    pdf.line(130, down2, 200, down2)

    pdf.x = 80
    pdf.y = down2
    pdf.set_font('timesbd', '', 13)
    pdf.multi_cell(50, 7, txt='Номер здания:', align='L')
    down3 = pdf.y
    pdf.x = 130
    pdf.y = down2
    pdf.set_font('times', '', 13)
    pdf.multi_cell(70, 7, txt=f'{building}', align='L')
    down3 = max(down3, pdf.y)
    pdf.line(130, down3, 200, down3)

    pdf.x = 80
    pdf.y = down3
    pdf.set_font('timesbd', '', 13)
    pdf.multi_cell(50, 7, txt='Номер договора:', align='L')
    down4 = pdf.y
    pdf.x = 130
    pdf.y = down3
    pdf.set_font('times', '', 13)
    pdf.multi_cell(70, 7, txt=f'{contract}', align='L')
    down4 = max(down4, pdf.y)
    pdf.line(130, down4, 200, down4)

    pdf.x = 80
    pdf.y = down4
    pdf.set_font('timesbd', '', 13)
    pdf.multi_cell(50, 7, txt='Наименование этапа работ по договору:', align='L')
    down5 = pdf.y
    pdf.x = 130
    pdf.y = down4
    pdf.set_font('times', '', 13)
    pdf.multi_cell(70, 7, txt=f'{contract_stage}', align='L')
    down5 = max(down5, pdf.y)
    pdf.line(130, down5, 200, down5)

    pdf.x = 80
    pdf.y = down5
    pdf.set_font('timesbd', '', 13)
    pdf.multi_cell(50, 7, txt='Вид документации:', align='L')
    down6 = pdf.y
    pdf.x = 130
    pdf.y = down5
    pdf.set_font('times', '', 13)
    pdf.multi_cell(70, 7, txt=f'{kind}', align='L')
    down6 = max(down6, pdf.y)
    pdf.line(130, down6, 200, down6)

    pdf.x = 80
    pdf.y = down6
    pdf.set_font('timesbd', '', 13)
    pdf.multi_cell(50, 7, txt='Марка/Раздел:', align='L')
    down7 = pdf.y
    pdf.x = 130
    pdf.y = down6
    pdf.set_font('times', '', 13)
    pdf.multi_cell(70, 7, txt=f'{mark}', align='L')
    pdf.line(130, down7, 200, down7)
    down7 = max(down7, pdf.y, downO)

    pdf.x = 10
    pdf.y = down7 + 10
    pdf.set_font('timesbd', '', 20)
    pdf.multi_cell(190, 7, txt=f'Задание №{task}', align='C')
    down8 = pdf.y

    pdf.x = 10
    pdf.y = down8 + 5
    pdf.set_font('timesbd', '', 13)
    pdf.cell(190, 7, txt='Содержание:', align='L')

    pdf.x = 10
    pdf.y = down8 + 15
    pdf.set_font('times', '', 13)
    pdf.multi_cell(190, 7, txt=f'{content}',
                   align='L')
    down9 = pdf.y

    pdf.y = down9 + 5
    pdf.set_font('timesbd', '', 13)
    pdf.cell(190, 7, txt='Состав задания:', align='L', ln=1)
    pdf.x = 20
    pdf.y += 5
    pdf.set_font('times', '', 13)
    pdf.multi_cell(190, 7, txt=f'{structure}')

    pdf.add_page()
    pdf.set_font('timesbd', '', 13)
    pdf.cell(190, 7, txt='Авторы задания:', align='L')
    down10 = pdf.y + 10
    pdf.x = 10
    pdf.y = down10
    pdf.set_font('times', '', 13)
    pdf.multi_cell(60, 7, txt=f'{ruk1_job_title}', align='L')
    down11 = pdf.y
    pdf.x = 75
    pdf.y = down10
    if ruk1_mark0:
        ruk1_mark = f'Подписано {ruk1_date}'
    else:
        if ruk1 != '':
            ruk1_mark = 'Не подписано'
        else:
            ruk1_mark = ''
    pdf.multi_cell(60, 7, txt=f'{ruk1_mark}', align='L', border='B')
    down11 = max(down11, pdf.y)
    pdf.x = 140
    pdf.y = down10
    pdf.multi_cell(60, 7, txt=f'{ruk1}', align='L')
    down11 = max(down11, pdf.y) + 5

    pdf.x = 10
    pdf.y = down11
    pdf.multi_cell(60, 7, txt=f'{ruk2_job_title}', align='L')
    down12 = pdf.y
    pdf.x = 75
    pdf.y = down11
    if ruk2_mark0:
        ruk2_mark = f'Подписано {ruk2_date}'
    else:
        if ruk2 != '':
            ruk2_mark = 'Не подписано'
        else:
            ruk2_mark = ''
    pdf.multi_cell(60, 7, txt=f'{ruk2_mark}', align='L', border='B')
    down12 = max(down12, pdf.y)
    pdf.x = 140
    pdf.y = down11
    pdf.multi_cell(60, 7, txt=f'{ruk2}', align='L')
    down12 = max(down12, pdf.y) + 5

    pdf.x = 10
    pdf.y = down12
    pdf.multi_cell(60, 7, txt=f'{isp_job_title}', align='L')
    down13 = pdf.y
    pdf.x = 75
    pdf.y = down12
    if isp_mark0:
        isp_mark = f'Подписано {isp_date}'
    else:
        if isp != '':
            isp_mark = 'Не подписано'
        else:
            isp_mark = ''
    pdf.multi_cell(60, 7, txt=f'{isp_mark}', align='L', border='B')
    down13 = max(down13, pdf.y)
    pdf.x = 140
    pdf.y = down12
    pdf.multi_cell(60, 7, txt=f'{isp}', align='L')
    down13 = max(down13, pdf.y) + 30
    pdf.x = 10
    pdf.y = down13 - 30
    pdf.cell(15, 7, txt='Тел.:')
    pdf.cell(30, 7, txt=f'{isp_phone}')

    pdf.x = 10
    pdf.y = down13 - 10
    pdf.set_font('timesbd', '', 13)
    pdf.cell(190, 7, txt='ОГИП:')
    pdf.x = 10
    pdf.y = down13
    pdf.set_font('times', '', 13)
    pdf.multi_cell(60, 7, txt=f'{cpe_job_title}', align='L')
    down14 = pdf.y
    pdf.x = 75
    pdf.y = down13
    if cpe_mark0:
        cpe_mark = f'Подписано {cpe_date}'
    else:
        if cpe != '':
            cpe_mark = 'Не подписано'
        else:
            cpe_mark = ''
    pdf.multi_cell(60, 7, txt=f'{cpe_mark}', align='L', border='B')
    down14 = max(down14, pdf.y)
    pdf.x = 140
    pdf.y = down13
    pdf.multi_cell(60, 7, txt=f'{cpe}', align='L')
    down14 = max(down14, pdf.y) + 30
    if cpe_comment != '':
        pdf.x = 10
        pdf.y = down14 - 25
        pdf.cell(190, 7, txt='Комментарий ГИПа:', ln=1)
        pdf.cell(190, 7, txt=f'{cpe_comment}')
        down14 = pdf.y + 30

    pdf.x = 10
    pdf.y = down14 - 10
    pdf.set_font('timesbd', '', 13)
    pdf.cell(190, 7, txt='Получатель задания:')
    pdf.x = 10
    pdf.y = down14
    pdf.set_font('times', '', 13)
    pdf.multi_cell(60, 7, txt=f'{getter_job_title}', align='L')
    down15 = pdf.y
    pdf.x = 75
    pdf.y = down14
    if getter_mark0:
        getter_mark = f'Подписано {getter_date}'
    else:
        if getter != '':
            getter_mark = 'Не подписано'
        else:
            getter_mark = ''
    pdf.multi_cell(60, 7, txt=f'{getter_mark}', align='L', border='B')
    down15 = max(down15, pdf.y)
    pdf.x = 140
    pdf.y = down14
    pdf.multi_cell(60, 7, txt=f'{getter}', align='L')
    down15 = max(down15, pdf.y) + 5
    if not os.path.exists(f"../monitoring_tasks/media/files/{task}"):
        os.makedirs(f"../monitoring_tasks/media/files/{task}")
    pdf.output(f"../monitoring_tasks/media/files/{task}/{task}.pdf")
