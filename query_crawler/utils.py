import datetime


def get_d_h_m_s(sec):
    td = datetime.timedelta(seconds=sec)
    m, s = divmod(td.seconds, 60)
    h, m = divmod(m, 60)
    v_list = [td.days, h, m, s]
    unit_list = ['日', '時間', '分', '秒']
    # to_text
    tt = lambda v, unit: f'{v}{unit}' if v > 0 else None
    text = ''.join([tt(v, unit)
                    for v, unit in zip(v_list, unit_list) if v > 0])
    return text
