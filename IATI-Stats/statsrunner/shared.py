def use_stat(stats, name):
    if hasattr(stats, 'enabled_stats'):
        return name in stats.enabled_stats
    else:
        return not name.startswith('_')
