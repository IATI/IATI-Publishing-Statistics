from collections import defaultdict, OrderedDict
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
        if type(obj.value) == datetime.date:
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
        elif (type(d1) != defaultdict and k not in d1):
            d1[k] = copy.deepcopy(v)
        elif type(d1[k]) in [int, decimal.Decimal, float]:
            d1[k] += v
        elif d1[k] is None:
            continue
        # else:
        #     try:
        #         d1[k] += v
        #     except:
        #         import pdb; pdb.set_trace()


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
        with open(os.path.join(output_dir, aggregate_name + '.json'), 'w') as fp:
            if aggregate_name == "by_hierarchy" and aggregate:
                json.dump(aggregate, fp, indent=2, default=decimal_default)
            else:
                try:
                    json.dump(aggregate, fp, sort_keys=True, indent=2, default=decimal_default)
                except TypeError:
                    fp.seek(0)
                    try:
                        date_aggregate = date_dict_builder(aggregate)
                        null_aggregate = null_dict(date_aggregate)
                        json.dump(null_aggregate, fp, sort_keys=True, indent=2, default=decimal_default)
                    except (AttributeError, TypeError):
                        null_aggregate = null_dict(aggregate)
                        json.dump(null_sorter(null_aggregate), fp, indent=2, default=decimal_default)
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
                        try:
                            stats_json = json.load(jsonfp, parse_float=decimal.Decimal)
                        except json.decoder.JSONDecodeError as e:
                            print(e)
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
                                   aggregate_name + '.json'), 'w') as fp:
                try:
                    json.dump(aggregate, fp, sort_keys=True, indent=2, default=decimal_default)
                except TypeError:
                    fp.seek(0)
                    date_aggregate = recursive_date_dict(aggregate)
                    json.dump(date_aggregate, fp, sort_keys=True, indent=2)

    all_stats = stats_module.AllDataStats()
    all_stats.aggregated = total
    for name, function in inspect.getmembers(all_stats, predicate=inspect.ismethod):
        if not statsrunner.shared.use_stat(all_stats, name):
            continue
        total[name] = function()

    for aggregate_name, aggregate in total.items():
        with open(os.path.join(args.output,
                               'aggregated',
                               aggregate_name + '.json'), 'w') as fp:
            try:
                json.dump(aggregate, fp, sort_keys=True, indent=2, default=decimal_default)
            except TypeError:
                fp.seek(0)
                date_aggregate = date_dict_builder(aggregate)
                json.dump(date_aggregate, fp, sort_keys=True, indent=2)


def date_dict_builder(obj):
    if type(obj) in [dict, defaultdict]:
        date_aggregate = {}
        for key, agg in obj.items():
            dates = {}
            for k, ag in agg.items():
                if type(k) == datetime.date:
                    dict_sum_inplace(dates, {k.strftime('%Y-%m-%d'): ag})
                elif type(ag) == datetime.date:
                    dict_sum_inplace(dates, {k: ag.strftime('%Y-%m-%d')})
            dict_sum_inplace(date_aggregate, {key: dates})
        return date_aggregate
    elif type(obj) == [datetime.date, datetime.datetime]:
        return obj.strftime('%Y-%m-%d')
    else:
        return None


def recursive_date_dict(obj):
    if type(obj) in [dict, defaultdict]:
        date_aggregate = {}
        for key, agg in obj.items():
            dict_sum_inplace(date_aggregate, {recursive_date_dict(key): recursive_date_dict(agg)})
        return date_aggregate
    elif type(obj) in [datetime.date, datetime.datetime]:
        return obj.strftime('%Y-%m-%d')
    else:
        return obj


def null_dict(obj):
    for key, agg in obj.items():
        if key is None:
            obj['null'] = obj.pop(key)
    return obj


def null_sorter(obj):
    for key in obj:
        if key == 'null':
            dict_to_sort = OrderedDict(obj)
            value = dict_to_sort.pop(key)
            sorted(dict_to_sort.items())
            dict_to_sort['null'] = value
            return dict_to_sort
    return sorted(obj.items())
