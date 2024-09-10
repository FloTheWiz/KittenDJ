# Two lonely functions. Useful though.

def get_length(milliseconds: int) -> str:
    total_seconds = milliseconds / 1000
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"


def bar(position, length):
    bar_char = '—'
    location_char = '⏵'
    bar_length = 15
    
    index = int((position / length) * bar_length)
    length_list = [bar_char] * bar_length
    length_list[index] = location_char
    return ''.join(length_list)
    
    