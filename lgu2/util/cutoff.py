
def get_cutoff(type: str) -> int:
    if type == 'ukpga':
        return 1988
    if type == 'uksi':
        return 1987
    if type == 'wsi':
        return 1999
    if type == 'nisi':
        return 1987
