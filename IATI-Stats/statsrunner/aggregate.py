from collections import defaultdict
import inspect
import json
import os
import copy
import decimal
import statsrunner
import datetime
from statsrunner import common


def decimal_default(obj):
    if hasattr(obj, 'value'):
        if type(obj.value) == datetime.datetime:
            return obj.value.strftime('%Y-%m-%d %H:%M:%S %z')
        else:
            return obj.value
    else:
        return common.decimal_default(obj)


def dict_sum_inplace(d1, d2):
    """Merge values from dictionary d2 into d1."""
    if d1 is None:
        return
    for k, v in d2.items():
        if type(v) == dict or type(v) == defaultdict:
            if k in d1:
                dict_sum_inplace(d1[k], v)
            else:
                d1[k] = copy.deepcopy(v)
        elif (type(d1) != defaultdict and not k in d1):
            d1[k] = copy.deepcopy(v)
        elif d1[k] is None:
            continue
        else:
            d1[k] += v


def make_blank(stats_module):
    """Return dictionary of stats functions for enabled stats_modules."""
    blank = {}
    for stats_object in [stats_module.ActivityStats(),
                         stats_module.ActivityFileStats(),
                         stats_module.OrganisationStats(),
                         stats_module.OrganisationFileStats(),
                         stats_module.PublisherStats(),
                         stats_module.AllDataStats()]:
        stats_object.blank = True
        for name, function in inspect.getmembers(stats_object, predicate=inspect.ismethod):
            if not statsrunner.shared.use_stat(stats_object, name):
                continue
            blank[name] = function()
    return blank


def aggregate_file(stats_module, stats_json, output_dir):
    """Create JSON file for each stats_module function."""
    subtotal = make_blank(stats_module)  # FIXME This may be inefficient
    for activity_json in stats_json['elements']:
        dict_sum_inplace(subtotal, activity_json)
    dict_sum_inplace(subtotal, stats_json['file'])

    try:
        os.makedirs(output_dir)
    except OSError:
        pass
    for aggregate_name, aggregate in subtotal.items():
        with open(os.path.join(output_dir, aggregate_name+'.json'), 'w') as fp:
            json.dump(aggregate, fp, sort_keys=True, indent=2, default=decimal_default)

    return subtotal


def aggregate(args):
    import importlib
    stats_module = importlib.import_module(args.stats_module)

    for newdir in ['aggregated-publisher', 'aggregated-file', 'aggregated']:
        try:
            os.mkdir(os.path.join(args.output, newdir))
        except OSError:
            pass

    blank = make_blank(stats_module)

    if args.verbose_loop:
        base_folder = os.path.join(args.output, 'loop')
    else:
        base_folder = os.path.join(args.output, 'aggregated-file')
    total = copy.deepcopy(blank)
    for folder in os.listdir(base_folder):
        publisher_total = copy.deepcopy(blank)

        for jsonfilefolder in os.listdir(os.path.join(base_folder, folder)):
            if args.verbose_loop:
                with open(os.path.join(base_folder, folder, jsonfilefolder)) as jsonfp:
                    stats_json = json.load(jsonfp, parse_float=decimal.Decimal)
                    subtotal = aggregate_file(stats_module,
                                              stats_json,
                                              os.path.join(args.output,
                                                           'aggregated-file',
                                                           folder,
                                                           jsonfilefolder))
            else:
                subtotal = copy.deepcopy(blank)
                for jsonfile in os.listdir(os.path.join(base_folder,
                                                        folder,
                                                        jsonfilefolder)):
                    with open(os.path.join(base_folder,
                                           folder,
                                           jsonfilefolder,
                                           jsonfile)) as jsonfp:
                        stats_json = json.load(jsonfp, parse_float=decimal.Decimal)
                        subtotal[jsonfile[:-5]] = stats_json

            dict_sum_inplace(publisher_total, subtotal)

        publisher_stats = stats_module.PublisherStats()
        publisher_stats.aggregated = publisher_total
        publisher_stats.folder = folder
        publisher_stats.today = args.today
        for name, function in inspect.getmembers(publisher_stats, predicate=inspect.ismethod):
            if not statsrunner.shared.use_stat(publisher_stats, name):
                continue
            publisher_total[name] = function()

        dict_sum_inplace(total, publisher_total)
        for aggregate_name, aggregate in publisher_total.items():
            try:
                os.mkdir(os.path.join(args.output, 'aggregated-publisher', folder))
            except OSError:
                pass
            with open(os.path.join(args.output,
                                   'aggregated-publisher',
                                   folder,
                                   aggregate_name+'.json'), 'w') as fp:
                json.dump(aggregate, fp, sort_keys=True, indent=2, default=decimal_default)

    all_stats = stats_module.AllDataStats()
    all_stats.aggregated = total
    for name, function in inspect.getmembers(all_stats, predicate=inspect.ismethod):
        if not statsrunner.shared.use_stat(all_stats, name):
            continue
        total[name] = function()

    for aggregate_name, aggregate in total.items():
        with open(os.path.join(args.output,
                               'aggregated',
                               aggregate_name+'.json'), 'w') as fp:
            json.dump(aggregate, fp, sort_keys=True, indent=2, default=decimal_default)
