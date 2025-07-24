from weasyprint import HTML
import json
import pymorphy3
import os
import uuid
import pathlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import matplotlib.transforms as mtrans

def load_json_data(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)

def declense_noun(noun, count):
    if isinstance(count, str):
        try:
            count = int(count)
        except ValueError:
            count = 0
    count_mod_10 = count % 10
    count_mod_100 = count % 100
    if noun == "прием":
        if count_mod_10 == 1 and count_mod_100 != 11:
            return "прием"
        elif count_mod_10 in [2, 3, 4] and count_mod_100 not in [12, 13, 14]:
            return "приема"
        else:
            return "приемов"
    elif noun == "ответ":
        if count_mod_10 == 1 and count_mod_100 != 11:
            return "ответ"
        elif count_mod_10 in [2, 3, 4] and count_mod_100 not in [12, 13, 14]:
            return "ответа"
        else:
            return "ответов"
    elif noun == "запрос":
        if count_mod_10 == 1 and count_mod_100 != 11:
            return "запрос"
        elif count_mod_10 in [2, 3, 4] and count_mod_100 not in [12, 13, 14]:
            return "запроса"
        else:
            return "запросов"
    elif noun == "обращение":
        if count_mod_10 == 1 and count_mod_100 != 11:
            return "обращение"
        elif count_mod_10 in [2, 3, 4] and count_mod_100 not in [12, 13, 14]:
            return "обращения"
        else:
            return "обращений"
    elif noun == "законопроект":
        if count_mod_10 == 1 and count_mod_100 != 11:
            return "законопроект"
        elif count_mod_10 in [2, 3, 4] and count_mod_100 not in [12, 13, 14]:
            return "законопроекта"
        else:
            return "законопроектов"
    elif noun == "встреча":
        if count_mod_10 == 1 and count_mod_100 != 11:
            return "встречу"
        elif count_mod_10 in [2, 3, 4] and count_mod_100 not in [12, 13, 14]:
            return "встречи"
        else:
            return "встреч"
    return noun

def generate_bar_chart(data):
    output_paths = []
    # Prepare and sort data
    categories = {
        "ЖКХ": data['citizen_requests']['requests'].get('utilities', 0),
        "Пенсии и выплаты": data['citizen_requests']['requests'].get('pensions_and_social_payments', 0),
        "Благоустройство": data['citizen_requests']['requests'].get('improvement', 0),
        "Образование": data['citizen_requests']['requests'].get('education', 0),
        "СВО": data['citizen_requests']['requests'].get('svo', 0),
        "Дороги": data['citizen_requests']['requests'].get('road_maintenance', 0),
        "Экология": data['citizen_requests']['requests'].get('ecology', 0),
        "Медицина": data['citizen_requests']['requests'].get('medicine_and_healthcare', 0),
        "Транспорт": data['citizen_requests']['requests'].get('public_transport', 0),
        "Несанкционированные \nсвалки": data['citizen_requests']['requests'].get('illegal_dumps', 0),
#        "Обращение\nк Председателю ЛДПР": data['citizen_requests']['requests'].get('appeals_to_ldpr_chairman', 0),
        "Юридическая помощь": data['citizen_requests']['requests'].get('legal_aid_requests', 0),
        "Развитие территорий": data['citizen_requests']['requests'].get('integrated_territory_development', 0),
        "Бесхозяйные животные  ": data['citizen_requests']['requests'].get('stray_animal_issues', 0),
        "Законодательные \nпредложения": data['citizen_requests']['requests'].get('legislative_proposals', 0)
    }
    
    # Найти максимальную длину строки с учётом переносов
    max_key_length = 0
    for key in categories.keys():
        lines = key.split('\n')
        max_line_length = max(len(line) for line in lines)
        max_key_length = max(max_key_length, max_line_length)

    # Дополнить пробелами каждую строку категории
    new_categories = {}
    for key, value in categories.items():
        lines = key.split('\n')
        padded_lines = [line.rstrip() + " " * (max_key_length - len(line.rstrip())) for line in lines]
        new_key = "\n".join(padded_lines)
        new_categories[new_key] = value
    categories = new_categories

    # Convert to integers and filter zero values
    categories = {k: int(v) if str(v).isdigit() else 0 for k, v in categories.items()}
    max_value = max(categories.values()) if categories.values() else 10  # Default max for empty data
    sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)

    for category, count in sorted_categories:
        chart_filename = f"tmp/chart_{uuid.uuid4()}.png"
        chart_abs_path = str(pathlib.Path.cwd() / chart_filename)
        output_paths.append(chart_abs_path)

        labels = [category]
        values = [count]

        # Colors setup
        colors = ['#394B8C']

        # Create figure with dynamic size, учитывая количество строк
        fig, ax = plt.subplots(figsize=(10, 0.4))
        ax.set_xlim([0.2, max_value * 1.1])
        # Create horizontal bars
        bars = ax.barh(labels, values, color=colors, height=0.6, edgecolor=colors, linewidth=2)

        for bar, value in zip(bars, values):
            if value >= 0:
                text_x = bar.get_width() * 0.95 if value > max_value / 15 else bar.get_width() + max_value * 0.02
                ha = 'right' if value > max_value / 15 else 'left'
                color = 'white' if value > max_value / 15 else 'black'
                ax.text(text_x, bar.get_y() + bar.get_height()/2, f'{int(value)}',
                        va='center', ha=ha, color=color, fontsize=14, fontweight='bold')

        # Customize axes
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)

        for i, (label, color) in enumerate(zip(labels, colors)):
            trans = mtrans.offset_copy(ax.get_yaxis_transform(), 
                y=0, fig=fig, units='points'
            )
            if "\n" in category:
                trans = mtrans.offset_copy(ax.get_yaxis_transform(), 
                    y=8, fig=fig, units='points'
                )

            ax.text(-0.01, i, label, ha='right', va='center', fontfamily='DejaVu Sans Mono',
                    color="black", fontsize=16, fontweight='bold', transform=trans,
                    bbox=dict(boxstyle='square,pad=0', edgecolor='none', facecolor='none', linewidth=0))
            ax.axhline(y=i-0.3, xmin=-0.64, xmax=0.1, color=color, linewidth=2, clip_on=False)

        plt.subplots_adjust(left=0.3, right=0.9, top=0.9, bottom=0.1)
        try:
            plt.savefig(chart_abs_path, dpi=300, bbox_inches='tight', transparent=True)
            plt.close()
        except Exception as e:
            print(f"Error saving chart image: {e}")
            raise
    return output_paths, sum(categories.values())


def generate_html_report(data):
    morph = pymorphy3.MorphAnalyzer()

    def format_list(items, singular, plural, case='nomn', item_format=lambda x: x):
        if not items:
            return f"не {plural}."
        count = len(items)
        if count == 1:
            noun = morph.parse(singular)[0].inflect({case, 'sing'}).word
            return f"{noun}: <ul class='list-disc pl-6'><li>{item_format(items[0])}</li></ul>"
        else:
            noun = morph.parse(plural)[0].inflect({case, 'plur'}).word
            items_html = ''.join(f'<li class="mb-2">{item_format(item)}</li>' for item in items)
            return f"{noun}: <ul class='list-disc pl-6'>{items_html}</ul>"

    def just_list(items, head, item_format=lambda x: x):
        if not items:
            return
        items_html = ''.join(f'<li class="mb-2">{item_format(item)}</li>' for item in items)
        return f"{head}: <ul class='list-disc pl-6'>{items_html}</ul>"

    # Format links
    links_text = just_list(
        data['general_info']['links'],
        "Ссылки на ресурсы",
        lambda x: f'<a href="{x}" class="text-ldpr-blue">{x}</a>'
    )
    committees_text = ''.join(f'<li class="mb-2">{item}</li>' for item in data['general_info']['committees'])
    committees_text = f"<ul class='list-disc pl-6'>{committees_text}</ul>"
    # Format legislation
    legislation_text = ""
    count = len(data['legislation'])
    if count == 0:
        legislation_text = "законопроекты за отчетный период не вносились."
    else:
        legislation_items = [
            f'<li class="mb-2"><strong>«{item["title"].strip()}»</strong>: {item["summary"].lower().strip()}. '
            f'<span>Статус: {item["status"]}.</span>'
            f'{"" if "rejection_reason" not in item or not item["rejection_reason"] else f" Причина отклонения: {item['rejection_reason']}."}</li>'
            for item in data['legislation']
        ]
        noun = "законопроект" if count == 1 else "законопроекты"
        local_noun = declense_noun("законопроект", count)

        legislation_text = f"Инициировал {count} {local_noun} из которых {sum(1 for item in data['legislation'] if item['status'].startswith('Внесен'))} внесены, {sum(1 for item in data['legislation'] if item['status'] == 'Принят')} приняты, {sum(1 for item in data['legislation'] if item['status'] == 'Отклонен')} отклонены. "
        legislation_text += f"В рамках законотворческой деятельности были внесены следующие {noun}:<ul class='list-disc pl-6'>{''.join(legislation_items)}</ul>"

    # Format citizen request examples
    examples_text = format_list(
        data['citizen_requests']['examples'],
        "достижение",
        "достижения",
        'nomn',
        lambda x: f'<span>{x["text"]}</span>'
    )

    # Format project activities
    project_activity_text = ""
    count = len(data['project_activity'])
    if count == 0:
        project_activity_text = "проекты и мероприятия за отчетный период не проводились."
    else:
        project_items = [
            f'<li class="mb-2"><strong>«{item["name"].strip()}»</strong>: {item["result"].lower().strip()}.</li>'
            for item in data['project_activity']
        ]
        proj_noun = "проект" if count == 1 else "проектов"
        event_noun = "мероприятие" if count == 1 else "мероприятий"
        project_activity_text = f"Среди реализованных {proj_noun} и {event_noun} можно выделить:<ul class='list-disc pl-6'>{''.join(project_items)}</ul>"

    # Format LDPR orders
    ldpr_orders_text = ""
    count = len(data['ldpr_orders'])
    if count == 0:
        ldpr_orders_text = "поручения Председателя ЛДПР за отчетный период отсутствуют."
    else:
        order_items = [
            f'<li class="mb-2"><strong>«{item["instruction"].strip()}»</strong>: {item["action"].lower().strip()}.</li>'
            for item in data['ldpr_orders']
        ]
        noun = "поручение" if count == 1 else "поручений"
        ldpr_orders_text = f"В рамках выполнения {noun} Председателя ЛДПР была проведена работа по следующим задачам:<ul class='list-disc pl-6'>{''.join(order_items)}</ul>"

    # Format SVO support projects (исправлено для работы с dict)
    svo_support_text = ""
    count = len(data['svo_support']['projects'])
    if count == 0:
        svo_support_text = "проекты по поддержке СВО за отчетный период не проводились."
    else:
        svo_items = [
            f'<li class="mb-2">{item.get("text", "").strip()}.</li>'
            for item in data['svo_support']['projects']
            if item.get("text")
        ]
        noun = "проект" if count == 1 else "проектов"
        svo_support_text = f"В рамках поддержки участников СВО и их семей были реализованы следующие {noun}:<ul class='list-disc pl-6'>{''.join(svo_items)}</ul>"

    # Manual declension for заседание
    def declense_zasedanie(count, prepositional=False):
        if isinstance(count, str):
            try:
                count = int(count)
            except ValueError:
                count = 0
        count_mod_10 = count % 10
        count_mod_100 = count % 100
        if prepositional:
            if count == 1:
                return "заседании"
            elif count_mod_10 in [2, 3, 4] and count_mod_100 not in [12, 13, 14]:
                return "заседания"
            else:
                return "заседаниях"
        else:
            if count_mod_10 == 1 and count_mod_100 != 11:
                return "заседание"
            elif count_mod_10 in [2, 3, 4] and count_mod_100 not in [12, 13, 14]:
                return "заседания"
            else:
                return "заседаний"



    sessions_total = declense_zasedanie(data['general_info']['sessions_attended']['total'])
    sessions_attended = declense_zasedanie(data['general_info']['sessions_attended']['attended'], prepositional=True)
    committee_total = declense_zasedanie(data['general_info']['sessions_attended']['committee_total'])
    committee_attended = declense_zasedanie(data['general_info']['sessions_attended']['committee_attended'], prepositional=True)
    ldpr_total = declense_zasedanie(data['general_info']['sessions_attended']['ldpr_total'])
    ldpr_attended = declense_zasedanie(data['general_info']['sessions_attended']['ldpr_attended'], prepositional=True)
    personal_meetings = declense_noun("прием", data['citizen_requests']['personal_meetings'])
    responses = declense_noun("ответ", data['citizen_requests']['responses'])
    official_queries = declense_noun("запрос", data['citizen_requests']['official_queries'])

    images_paths, requests_count = generate_bar_chart(data)
    images_text = "".join(f'<img src="file://{image_path}" style="max-width: 100%; height: auto;">' for image_path in images_paths)
    ldpr_requests_text = f"""
    <p class="mt-4 big"><strong>Получено обращений на имя Председателя ЛДПР: <b>{data['citizen_requests']['requests'].get('appeals_to_ldpr_chairman', 0)}</b></strong></p>
    """ if int(data['citizen_requests']['requests'].get('appeals_to_ldpr_chairman', 0)) > 0 else ""
    meeting_noun = declense_noun("встреча", sum(data["citizen_day_receptions"].values()))
    citizen_requests_text = f"""
    <p class="mb-4">Депутат провел <strong>{data['citizen_requests']['personal_meetings']}</strong> личных {personal_meetings} граждан в том числе {sum(data["citizen_day_receptions"].values())} {meeting_noun} в рамках Всероссийского дня приема граждан. За отчетный период поступило множество письменных обращений, охватывающих различные тематики:</p>
    <div class="table-container">
        <h4>Тематика обращений граждан</h4>
        {images_text}
    </div>
    {ldpr_requests_text}
    <p class="mt-4">На обращения граждан было дано <strong>{data['citizen_requests']['responses']}</strong> {responses}, а также направлено <strong>{data['citizen_requests']['official_queries']}</strong> депутатских {official_queries} в органы власти и иные организации. Среди примеров успешной работы можно отметить: {examples_text}</p>
    """
    other_info_text = f"""
            <div class="section-container other_info">
                <h3>7. ИНАЯ ЗНАЧИМАЯ ИНФОРМАЦИЯ</h3>
                <div>
                    <p>{data['other_info'].strip()}.</p>
                </div>
            </div>
    """ if data['other_info'].strip() else ""
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>ОТЧЕТ ДЕЯТЕЛЬНОСТИ ДЕПУТАТА ЛДПР</title>
        <link href="https://fonts.googleapis.com/css2?family=Geologica:wght@400;500;600&display=swap" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&display=swap" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/meyer-reset/2.0/reset.min.css" rel="stylesheet">
        <style>
            * {{ -webkit-font-smoothing: antialiased; box-sizing: border-box; }}
            body {{ font-family: 'Geologica', sans-serif; font-size: 14px; line-height: 15.2px; color: #000000; background: #FFFFFF; margin: 0; height: 100%;
            width: 21cm;}}
            .big {{font-size: 18px}}
            .container {{ width: 720px; margin: 0 auto; padding: 0 24px; margin-top: 40px; }}
            .ldpr-yellow {{ background-color: #FFC531; }}
            .ldpr-blue {{ color: #394B8C; }}
            .text-ldpr-blue {{ color: #394B8C; text-decoration: underline; }}
            .status-green {{ color: #097903; }}
            .status-red {{ color: #FF0000; }}
            .header {{
                position: relative;
                text-align: center;
                background: #394B8C;
                color: #FFFFFF;
                margin-bottom: 12px;
                border-radius: 0 0 20px 20px;
                height: 171.4px; /* Фиксированная высота для согласованности */
                padding-top: 20px;
                padding-bottom: 20px;
            }}             
           .header-content {{
                flex-grow: 1;
                padding: 0 20px;
            }}
            .header h1 {{ font-family: 'Geologica', sans-serif; font-size: 44px; font-weight: 400; text-transform: uppercase; line-height: 44px; margin-bottom: 6px; font-weight: 700;}}
            .header h2 {{ font-family: 'Geologica', sans-serif; font-weight: 600; font-size: 16px; line-height: 17px; margin-top: 8px;}}
            .header p {{ font-family: 'Geologica', sans-serif; font-weight: 400; font-size: 12px; line-height: 14.4px; text-align: center; }}
            .section-container {{ margin-bottom: 29px; position: relative; }}
            h3 {{ font-family: 'Geologica', sans-serif; font-weight: 600; font-size: 26px; line-height: 22px; color: #000000; background: #FFC531; padding: 3px 0; margin-bottom: 20px; width: 100%; }}
            h4 {{ text-align: center; }}
            p {{ margin: 0 0 6px 0; text-align: justify; font-family: 'Geologica', sans-serif; font-weight: 400; font-size: 14.0px; line-height: 15.2px; }}
            ul.list-disc {{ margin: 7px 0 6px 0; padding-left: 20px; list-style: none; }}
            ul.list-disc li {{ position: relative; padding-left: 20px; list-style-type: none; }}
            ul.list-disc li::before {{ content: ''; background-image: url("data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjYiIGhlaWdodD0iNjIiIHZpZXdCb3g9IjAgMCA2NiA2MyIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTM1Ljk1NTYgMjcuOTQyM0w0MC4yOTg2IDAuMzgwODU5SDI1LjI2NTFMMjkuNjA4MSAyNy45NDIzTDQuNzE5MzEgMTUuNDE0NEwwLjA0MjIxMzQgMjkuNjEyN0wyNy40MzY2IDM0LjI4OThMNy44OTMwNSA1My44MzMzTDE5LjkxOTkgNjIuNjg2NEwzMi43ODE4IDM3Ljk2NDZMNDUuNjQzOSA2Mi42ODY0TDU3LjY3MDcgNTMuODMzM0wzOC4xMjcxIDM0LjI4OThMNjUuNTIxNSAyOS42MTI3TDYwLjg0NDQgMTUuNDE0NEwzNS45NTU2IDI3Ljk0MjNaIiBmaWxsPSIjRkRDNDJFIi8+Cjwvc3ZnPgo="); background-repeat: no-repeat; background-size: contain; position: absolute; left: 0; width: 12px; height: 12px; top: 3px; }}
            a {{ color: #394B8C; text-decoration: underline; }}
            .table-container {{ background: #EAF1F9; border-radius: 20px; margin: 15px 0; padding: 10px; padding-left: 20px; text-align: center; }}
            strong {{ font-weight: 600; }}
            b {{ font-weight: 900; }}
            @page {{ size: A4; margin: 1cm 0cm 1cm 0cm; }}
            @page :first {{ margin: 0cm 0cm 1cm 0cm; }}
            @page {{ @bottom-right {{ content: counter(page) " / " counter(pages); font-family: 'Geologica', sans-serif; border-top-left-radius: 6px; font-size: 10px; color: #FFFFFF; background: #394B8C; height: 20px; line-height: 0px; padding-left: 8px; padding-right: 8px; text-align: center; margin-top: 20px; }} }}
.header-decoration {{
    position: absolute;
    top: 0;
    width: 171.4px;
    height: 171.4px;
}}
.header-decoration.left {{
    left: 0;
}}
.header-decoration.right {{
    right: 0;
}}
.header-decoration img {{
    height: 100%;
    width: 100%;
    display: block; /* Убирает возможные отступы */
}}
.header-decoration.left img {{
    border-radius: 0 0 0 20px;
}}

.header-decoration.right img {{
    border-radius: 0 0 20px 0;
}}

.header-content {{
}}
        </style>
    </head>
    <body>
<div class="header">
    <div class="header-decoration left"></div>
    <div class="header-decoration right">
        <img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNTQwIiBoZWlnaHQ9IjU0MCIgdmlld0JveD0iMCAwIDU0MCA1NDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxnIGNsaXAtcGF0aD0idXJsKCNjbGlwMF8yMDY2XzM2NikiPgo8cGF0aCBkPSJNMCAzOTBDMCAzMjMuNzI2IDUzLjcyNTggMjcwIDEyMCAyNzBIMjcwVjU0MEgwVjM5MFoiIGZpbGw9IiNDQ0Q4RTgiLz4KPHBhdGggZD0iTTI3MCAxMjBDMjcwIDIwMi84NDMgMzM3LjE1NyAyNzAgNDIwIDI3MEg1NDBWMEgyNzBWMTIwWiIgZmlsbD0iIzIzMjI1QiIvPgo8cGF0aCBkPSJNNTQwIDU0MFYyNzBIMjcwVjU0MEg1NDBaIiBmaWxsPSIjRkZDNTMxIi8+CjxwYXRoIGZpbGwtcnVsZT0iZXZlbm9kZCIgY2xpcC1ydWxlPSJldmVub2RkIiBkPSJNMjcwIDQ0OUMyNzAgMzUwLjE0MSAxODkuODU5IDI3MCA5MSAyNzBDMTg5Ljg1OSAyNzAgMjc0IDE4OS44NTkgMjcwIDkxQzI3MCAxODkuODU5IDM1MC4xNDEgMjc0IDQ0OSAyNzBDMzUwLjE0MSAyNzAgMjc0IDM1MC4xNDEgMjcwIDQ0OVoiIGZpbGw9IndoaXRlIi8+CjwvZz4KPGRlZnM+CjxjbGlwUGF0aCBpZD0iY2xpcDBfMjA2Nl8zNjYiPgo8cmVjdCB3aWR0aD0iNTQwIiBoZWlnaHQ9IjU0MCIgZmlsbD0id2hpdGUiLz4KPC9jbGlwUGF0aD4KPC9kZWZzPgo8L3N2Zz4K" alt="Right decoration">
    </div>
    <div class="header-content">
        <h1>ОТЧЕТ О ПРОДЕЛАННОЙ <br> РАБОТЕ ДЕПУТАТА</h1>
        <h2>{data['general_info']['full_name']}</h2>
        <p>за I полугодие 2025 года</p>
    </div>
</div>

        <div class="container">
            <div class="section-container">
                <h3>1. ОБЩАЯ ИНФОРМАЦИЯ</h3>
                <div>
                    <p>ФИО: <strong>{data['general_info']['full_name']}</strong></p>
                    <p>Избирательный округ: {data['general_info']['district'].strip()}</p>
                    <p>Срок полномочий: {data['general_info']['term_start']} - {data['general_info']['term_end']}</p>
                    <p>Должность: {data['general_info']['position']}</p>
                    <p>Должность во фракции ЛДПР: {data['general_info']['ldpr_position']}</p>
                    <p>Комитеты и комиссии, в которых состоит:</p>
                    {committees_text}
                    <p class="mb-4">Участие в заседаниях:</p>
                    <ul class="list-disc">
                        <li>Заседания органа власти: присутствовал на {data['general_info']['sessions_attended']['attended']} из {data['general_info']['sessions_attended']['total']} {sessions_total}.</li>
                        <li>Заседания комитетов: присутствовал на {data['general_info']['sessions_attended']['committee_attended']} из {data['general_info']['sessions_attended']['committee_total']} {committee_total}.</li>
                        <li>Заседания фракции ЛДПР: присутствовал на {data['general_info']['sessions_attended']['ldpr_attended']} из {data['general_info']['sessions_attended']['ldpr_total']} {ldpr_total}.</li>
                    </ul>
                    {links_text}
                </div>
            </div>

            <div class="section-container">
                <h3>2. ЗАКОНОТВОРЧЕСКАЯ ДЕЯТЕЛЬНОСТЬ</h3>
                <div>
                    <p>{legislation_text}</p>
                </div>
            </div>

            <div class="section-container">
                <h3>3. РАБОТА С ОБРАЩЕНИЯМИ ГРАЖДАН</h3>
                <div>
                    {citizen_requests_text}
                </div>
            </div>

            <div class="section-container">
                <h3>4. ПОДДЕРЖКА УЧАСТНИКОВ СВО И ИХ СЕМЕЙ</h3>
                <div>
                    <p>{svo_support_text}</p>
                </div>
            </div>

            <div class="section-container">
                <h3>5. ПРЕДСТАВИТЕЛЬСКАЯ И ПРОЕКТНАЯ ДЕЯТЕЛЬНОСТЬ</h3>
                <div>
                    <p>{project_activity_text}</p>
                </div>
            </div>

            <div class="section-container">
                <h3>6. РАБОТА ПО ПОРУЧЕНИЯМ ПРЕДСЕДАТЕЛЯ ЛДПР</h3>
                <div>
                    <p>{ldpr_orders_text}</p>
                </div>
            </div>
            {other_info_text}
        </div>
    </body>
    </html>
    """

    return html_content, images_paths


def generate_pdf_report(json_data, output_filename, debug=False):
    html_content, images_paths = generate_html_report(json_data)

    try:
        HTML(string=html_content).write_pdf(output_filename)
        if debug:
            with open("debug.html", "w", encoding="utf-8") as f:
                f.write(html_content)
    finally:
        for image_path in images_paths:
            if os.path.exists(image_path):
                os.remove(image_path)

if __name__ == "__main__":
    input_file = "ldpr_report_слуцкий_леонид_эдуардович_2025_07_24_5.json"
    output_file = "ldpr_report_слуцкий_леонид_эдуардович_2025_07_24_5.pdf"

    json_data = load_json_data(input_file)
    generate_pdf_report(json_data, output_file, True)

