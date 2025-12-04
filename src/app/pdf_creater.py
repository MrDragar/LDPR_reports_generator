from weasyprint import HTML
import json
import pymorphy3
import os
import uuid
import pathlib
import matplotlib.pyplot as plt
import matplotlib.transforms as mtrans

def load_json_data(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)

def delete_dot(string):
    if not string or string[-1] != ".":
        return string
    return string[:-1]

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
        if count == 0:
            continue
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
        items_html = ''.join(f'<li class="mb-2 small">{item_format(item)}</li>' for item in items)
        return f"{head}: <ul class='list-disc pl-6'>{items_html}</ul>"

    # Format links
    links_text = just_list(
        data['general_info']['links'],
        "Ссылки на ресурсы",
        lambda x: f'<a href="{x}" class="text-ldpr-blue">{x}</a>'
    ) if data['general_info']['links'] and len(data['general_info']['links']) != 1 and data['general_info']['links'][0] else ""
    committees_text = ''.join(f'<li class="mb-2 small">{item}</li>' for item in data['general_info']['committees'])
    committees_text = f"<ul class='list-disc pl-6'>{committees_text}</ul>"
    committees_text = f"<p>Комитеты и комиссии, в которых состоит:</p> {committees_text}" if data['general_info']['committees'] and len(data['general_info']['committees']) != 1 and data['general_info']['committees'][0] else ""
    # Format legislation
    legislation_text = ""
    count = len(data['legislation'])
    if count == 0:
        legislation_text = "законопроекты за отчетный период не вносились."
    else:
        legislation_items = [
            f'<li class="mb-2"><strong>«{item["title"].strip()}»</strong>: {delete_dot(item["summary"].strip())}. '
            f'<span>Статус: {item["status"]}.</span>'
            f'{"" if "rejection_reason" not in item or not item["rejection_reason"] else f" Причина отклонения: {delete_dot(item['rejection_reason'])}."}</li>'
            for item in data['legislation']
        ]
        noun = "законопроект" if count == 1 else "законопроекты"
        local_noun = declense_noun("законопроект", count)

        # legislation_text = f"Инициировал {count} {local_noun} из которых внесено — {sum(1 for item in data['legislation'] if item['status'].startswith('Внесен'))}, принято — {sum(1 for item in data['legislation'] if item['status'] == 'Принят')}, отклонено — {sum(1 for item in data['legislation'] if item['status'] == 'Отклонен')}. "
        legislation_text = f"Внесено по инициативе ЛДПР — {sum(1 for item in data['legislation'] if item['status'] == 'внесено по инициативе ЛДПР')}, внесено межфракционно —  {sum(1 for item in data['legislation'] if item['status'] == 'внесено по инициативе ЛДПР')}. Из них принято по инициативе ЛДПР — {sum(1 for item in data['legislation'] if item['status'] == 'Принято по инициативе ЛДПР')}, принято межфракционно — {sum(1 for item in data['legislation'] if item['status'] == 'Принято межфракционно')}, отклонено — {sum(1 for item in data['legislation'] if item['status'] == 'Отклонен')}. "
        legislation_text += f"<ul class='list-disc pl-6'>{''.join(legislation_items)}</ul>"

    # Format citizen request examples
    examples_text = format_list(
        data['citizen_requests']['examples'],
        "достижение",
        "достижения",
        'nomn',
        lambda x: f'<span>{delete_dot(x["text"])}.</span>'
    )

    # Format project activities
    project_activity_text = ""
    count = len(data['project_activity'])
    if count == 0:
        project_activity_text = "проекты и мероприятия за отчетный период не проводились."
    else:
        project_items = [
            f'<li class="mb-2"><strong>«{item["name"].strip()}»</strong>: {delete_dot(item["result"].strip())}.</li>'
            for item in data['project_activity']
        ]
        proj_noun = "проект" if count == 1 else "проектов"
        event_noun = "мероприятие" if count == 1 else "мероприятий"
        project_activity_text = f"<ul class='list-disc pl-6'>{''.join(project_items)}</ul>"

    # Format LDPR orders
    ldpr_orders_text = ""
    count = len(data['ldpr_orders'])
    if count == 0:
        ldpr_orders_text = "поручения Председателя ЛДПР за отчетный период отсутствуют."
    else:
        order_items = [
            f'<li class="mb-2"><strong>«{item["instruction"].strip()}»</strong>: {delete_dot(item["action"].strip())}.</li>'
            for item in data['ldpr_orders']
        ]
        noun = "поручение" if count == 1 else "поручений"
        ldpr_orders_text = f"<ul class='list-disc pl-6'>{''.join(order_items)}</ul>"

    # Format SVO support projects (исправлено для работы с dict)
    svo_support_text = ""
    count = len(data['svo_support']['projects'])
    if count == 0:
        svo_support_text = "проекты по поддержке СВО за отчетный период не проводились."
    else:
        svo_items = [
            f'<li class="mb-2">{delete_dot(item.get("text", "").strip())}.</li>'
            for item in data['svo_support']['projects']
            if item.get("text")
        ]
        noun = "проект" if count == 1 else "проектов"
        svo_support_text = f"<ul class='list-disc pl-6'>{''.join(svo_items)}</ul>"

    # Manual declension for заседание
    def declense_zasedanie(count, prepositional=False):
        if isinstance(count, str):
            try:
                count = int(count)
            except ValueError:
                count = 0
        count_mod_10 = count % 10
        count_mod_100 = count % 100
        if count == 1:
            return "заседания"
        elif count_mod_10 == 1 and count != 11:
            return "заседания"
        else:
            return "заседаний"



    sessions_total = declense_zasedanie(data['general_info']['sessions_attended']['total'])
    committee_total = declense_zasedanie(data['general_info']['sessions_attended']['committee_total'])
    ldpr_total = declense_zasedanie(data['general_info']['sessions_attended']['ldpr_total'])

    personal_meetings = declense_noun("прием", data['citizen_requests']['personal_meetings'])
    responses = declense_noun("ответ", data['citizen_requests']['responses'])
    official_queries = declense_noun("запрос", data['citizen_requests']['official_queries'])

    images_paths, requests_count = generate_bar_chart(data)
    images_text = "".join(f'<img src="file://{image_path}" style="max-width: 100%; height: auto;">' for image_path in images_paths)
    ldpr_requests_text = f"""
    <p class="mt-4 big"><strong>Получено обращений на имя Председателя ЛДПР: <b>{data['citizen_requests']['requests'].get('appeals_to_ldpr_chairman', 0)}</b></strong></p>
    """ if int(data['citizen_requests']['requests'].get('appeals_to_ldpr_chairman', 0)) > 0 else ""
    meeting_noun = declense_noun("встреча", sum(data['citizen_requests']["citizen_day_receptions"].values()))
    citizen_requests_text = f"""
    <p class="mb-4">Депутат провел <strong>{data['citizen_requests']['personal_meetings']}</strong> личных {personal_meetings} граждан в том числе {sum(data['citizen_requests']["citizen_day_receptions"].values())} {meeting_noun} в рамках Всероссийского дня приема граждан. За отчетный период поступило множество письменных обращений, охватывающих различные темы:</p>
    <div class="table-container">
        {images_text}
    </div>
    {ldpr_requests_text}
    <p class="mt-4">На обращения граждан было дано <strong>{data['citizen_requests']['responses']}</strong> {responses}, а также направлено <strong>{data['citizen_requests']['official_queries']}</strong> депутатских {official_queries} в органы власти и иные организации. Среди примеров успешной работы можно отметить {examples_text}</p>
    """
    while "\\n" in data['other_info']:
        data['other_info'] = data['other_info'].replace("\\n", "<br>")

    while "\n" in data['other_info']:
        data['other_info'] = data['other_info'].replace("\n", "<br>")

    other_info_text = f"""
            <div class="section-container other_info">
                <h3>7. ИНАЯ ЗНАЧИМАЯ ИНФОРМАЦИЯ</h3>
                <div>
                    <p>{delete_dot(data['other_info'].strip())}.</p>
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
                margin-right: 140px
            }}
            .header-content h1.first {{ font-family: 'Geologica', sans-serif; font-size: 44px; font-weight: 400; text-transform: uppercase; line-height: 44px; margin-bottom: 6px; font-weight: 700;}}
            .header h1.second {{ font-family: 'Geologica', sans-serif; font-size: 44px; font-weight: 400; text-transform: uppercase; line-height: 44px; margin-bottom: 6px; font-weight: 700;}}
            .header h2 {{ font-family: 'Geologica', sans-serif; font-weight: 600; font-size: 16px; line-height: 17px; margin-top: 8px;}}
            .header p {{ font-family: 'Geologica', sans-serif; font-weight: 400; font-size: 12px; line-height: 14.4px; text-align: center; }}
            .section-container {{ margin-bottom: 29px; position: relative; }}
            h3 {{ font-family: 'Geologica', sans-serif; font-weight: 600; font-size: 26px; line-height: 22px; color: #000000; background: #87CEEB; padding: 3px 0; margin-bottom: 20px; width: 100%; }}
            h4 {{ text-align: center; }}
            p {{ 
                margin: 0 0 6px 0; 
                # text-align: justify; 
                font-family: 'Geologica',
                sans-serif; font-weight: 400;
                font-size: 14.0px; line-height: 15.2px; 
            }}
            ul.list-disc {{ margin: 7px 0 6px 0; padding-left: 20px; list-style: none; }}
            ul.list-disc li {{ position: relative; padding-left: 20px; list-style-type: none; padding-bottom: 10px}}
            ul.list-disc li.small {{ padding-bottom: 0px}}
            ul.list-disc li::before {{
  content: ''; 
  background-image: url("data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjYiIGhlaWdodD0iNjIiIHZpZXdCb3g9IjAgMCA2NiA2MyIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTM1Ljk1NTYgMjcuOTQyM0w0MC4yOTg2IDAuMzgwODU5SDI1LjI2NTFMMjkuNjA4MSAyNy45NDIzTDQuNzE5MzEgMTUuNDE0NEwwLjA0MjIyMTM0IDI5LjYxMjdMMjcuNDM2NiAzNC4yODk4TDcuODkzMDUgNTMuODMzM0wxOS45MTk5IDYyLjY4NjRMMzIuNzgxOCAzNy45NjQ2TDQ1LjY0MzkgNjIuNjg2NEw1Ny42NzA3IDUzLjgzMzNMMzguMTI3MSAzNC4yODk4TDY1LjUyMTUgMjkuNjEyN0w2MC44NDQ0IDE1LjQxNDRMMzUuOTU1NiAyNy45NDIzWiIgZmlsbD0iIzNCODJGNiIvPgo8L3N2Zz4K"); 
  background-repeat: no-repeat; 
  background-size: contain; 
  position: absolute; 
  left: 0; 
  width: 12px; 
  height: 12px; 
  top: 3px; 
}}
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
        <img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNTQwIiBoZWlnaHQ9IjU0MCIgdmlld0JveD0iMCAwIDU0MCA1NDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGcgY2xpcC1wYXRoPSJ1cmwoI2NsaXAwXzIwNjZfMzY2KSI+PHBhdGggZD0iTTAgMzkwQzAgMzIzLjcyNiA1My43MjU4IDI3MCAxMjAgMjcwSDI3MFY1NDBIMFYzOTBaIiBmaWxsPSIjQ0NEOEU4Ii8+PHBhdGggZD0iTTI3MCAxMjBDMjcwIDIwMi84NDMgMzM3LjE1NyAyNzAgNDIwIDI3MEg1NDBWMEgyNzBWMTIwWiIgZmlsbD0iIzM5NEI4QyIvPjxwYXRoIGQ9Ik01NDAgNTQwVjI3MEgyNzBWNTQwSDU0MFoiIGZpbGw9IiNGRkM1MzEiLz48cGF0aCBmaWxsLXJ1bGU9ImV2ZW5vZGQiIGNsaXAtcnVsZT0iZXZlbm9kZCIgZD0iTTI3MCA0NDlDMjcwIDM1MC4xNDEgMTg5Ljg1OSAyNzAgOTEgMjcwQzE4OS44NTkgMjcwIDI3NCAxODkuODU5IDI3MCA5MUMyNzAgMTg5Ljg1OSAzNTAuMTQxIDI3NCA0NDkgMjcwQzM1MC4xNDEgMjcwIDI3NCAzNTAuMTQxIDI3MCA0NDlaIiBmaWxsPSJ3aGl0ZSIvPjwvZz48ZGVmcz48Y2xpcFBhdGggaWQ9ImNsaXAwXzIwNjZfMzY2Ij48cmVjdCB3aWR0aD0iNTQwIiBoZWlnaHQ9IjU0MCIgZmlsbD0id2hpdGUiLz48L2NsaXBQYXRoPjwvZGVmcz48L3N2Zz4=" alt="Right decoration">
    </div>
    <div class="header-content">
        <h1 class="first">ОТЧЕТ О ПРОДЕЛАННОЙ</h1> 
        <h1 class="second">РАБОТЕ ДЕПУТАТА ЛДПР</h1>
        <h2>{data['general_info']['full_name']}</h2>
        <p>по итогам осенней сессии 2025 года</p>
    </div>
</div>

        <div class="container">
            <div class="section-container">
                <h3>1. ОБЩАЯ ИНФОРМАЦИЯ</h3>
                <div>
                    <p>ФИО: <strong>{data['general_info']['full_name']}</strong></p>
                    <p>Избирательный округ: {data['general_info']['district'].strip()}</p>
                    <p>Субъект Российской Федерации: {data['general_info']['region'].strip()}</p>
                    <p>Представительный орган власти: {data['general_info']['authority_name'].strip()}</p>
                    <p>Срок полномочий: {data['general_info']['term_start']} - {data['general_info']['term_end']}</p>
                    <p>Должность: {data['general_info']['position']}</p>
                    <p>Должность во фракции ЛДПР: {data['general_info']['ldpr_position']}</p>
                    {committees_text}
                    <p class="mb-4">Участие в заседаниях:</p>
                    <ul class="list-disc">
                        <li class="small">Заседания органа власти: присутствовал на {data['general_info']['sessions_attended']['attended']} из {data['general_info']['sessions_attended']['total']} {sessions_total}.</li>
                        <li class="small">Заседания комитетов: присутствовал на {data['general_info']['sessions_attended']['committee_attended']} из {data['general_info']['sessions_attended']['committee_total']} {committee_total}.</li>
                        <li class="small">Заседания фракции ЛДПР: присутствовал на {data['general_info']['sessions_attended']['ldpr_attended']} из {data['general_info']['sessions_attended']['ldpr_total']} {ldpr_total}.</li>
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
    input_file = "report_ldpr_Абдель_Щеняй_Ярослав.json"
    output_file = "report_ldpr_Абдель_Щеняй_Ярослав.pdf"

    json_data = load_json_data(input_file)
    generate_pdf_report(json_data, output_file, True)

