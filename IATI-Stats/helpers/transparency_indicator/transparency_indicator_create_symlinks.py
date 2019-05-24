import os

endorsers = {
    'afdb': ['afdb'],
    'asdb': ['asdb'],
    'ausaid': ['ausaid'],
    'dfatd-maecd': ['dfatd-maecd'],
    'danida': ['danida'],
    'eu': ['eu',
        'ec-echo',
        'ec-elarg',
        'ec-fpi'],
    'finland_mfa': ['finland_mfa'],
    'gavi': ['gavi'],
    'bmz': ['bmz'],
    'iadb': ['iadb'],
    'irishaid': ['irishaid'], # FIXME
    'minbuza_nl': ['minbuza_nl'],
    'mfat': ['mfat'],
    'maec': ['maec'],
    'sida': ['sida'],
    'sdc_ch': ['sdc_ch'],
    'theglobalfund': ['theglobalfund'],
    'worldbank': ['worldbank'],
    'uk': ['dfid',
        'fco',
        'deccadmin',
        'dwp',
        'doh',
        'hooda'],
    'unhabitat': ['unhabitat'],
    'unicef': ['unicef'],
    'undp': ['undp'],
    'unops': ['unops'],
    'unfpa': ['unfpa'],
    'wfp': ['wfp'],
    'unitedstates': ['unitedstates'],
    'unw': ['unw']
}

for endorser, publishers in endorsers.items():
    try:
        os.makedirs(os.path.join('data-ti',endorser))
        for publisher in publishers:
            #for f in os.listdir(os.path.join('data-full',publisher)):
            os.symlink(os.path.join('..','..','data-full',publisher), os.path.join('data-ti',endorser,publisher))
    except OSError:
        pass
