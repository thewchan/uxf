#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

import contextlib
import filecmp
import gzip
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import time

try:
    os.chdir(os.path.dirname(__file__)) # move to this file's dir
    sys.path.append('..')
    import uxf
    import eq
    UXF_EXE = os.path.abspath('../uxf.py')
    UXFCONVERT_EXE = os.path.abspath('../uxfconvert.py')
    SLIDES1 = os.path.abspath('../eg/slides1.py')
    SLIDES2 = os.path.abspath('../eg/slides2.py')
    SLIDES_SLD = os.path.abspath('../eg/slides.sld')
    TEST_CONVERTERS = os.path.abspath('../t/test_converters.py')
    TEST_SQLITE = os.path.abspath('../t/test_sqlite.py')
    TEST_ERRORS = os.path.abspath('../t/test_errors.py')
    TEST_LINTS = os.path.abspath('../t/test_lints.py')
    os.chdir('../../testdata') # move to test data
finally:
    pass


def main():
    max_total, verbose = get_config()
    cleanup()
    t = time.monotonic()
    uxffiles = sorted((name for name in os.listdir('.')
                       if os.path.isfile(name) and name.endswith(
                           ('.uxf', '.uxf.gz'))),
                      key=by_number)
    print('.', end='', flush=True)
    total = ok = 0
    total, ok = test_uxf_files(uxffiles, verbose=verbose,
                               max_total=max_total)
    total, ok = test_uxf_loads_dumps(uxffiles, total, ok, verbose=verbose,
                                     max_total=max_total)
    total, ok = test_uxf_equal(uxffiles, total, ok, verbose=verbose,
                               max_total=max_total)
    total, ok = test_uxfconvert(uxffiles, total, ok, verbose=verbose,
                                max_total=max_total)
    total, ok = test_table_is_scalar(total, ok, verbose=verbose)
    total, ok = test_slides(SLIDES1, total, ok, verbose=verbose)
    total, ok = test_slides(SLIDES2, total, ok, verbose=verbose)
    for cmd in (TEST_CONVERTERS, TEST_SQLITE, TEST_ERRORS, TEST_LINTS):
        total, ok = test_external([cmd, '--regression'], total, ok,
                                  verbose=verbose)
    if total < 150:
        print('\b' * total, end='', flush=True)
    if total == ok:
        t = time.monotonic() - t
        print(f'{ok}/{total} All OK ({t:.3f} sec)')
        cleanup()
    else:
        print(f'{ok}/{total} FAIL')


def get_config():
    verbose = False
    max_total = 999999
    for arg in sys.argv[1:]:
        if arg in {'-h', '--help'}:
            raise SystemExit('usage: regression.py [-v|--verbose] [max]')
        elif arg in {'-v', '--verbose'}:
            verbose = True
        elif arg.isdecimal():
            max_total = int(arg)
    return max_total, verbose


def test_uxf_files(uxffiles, *, verbose, max_total):
    total = ok = 0
    for name in uxffiles:
        total += 1
        if total > max_total:
            return total - 1, ok
        actual = f'actual/{name}'
        expected = f'expected/{name}'
        if expected.endswith('.gz'):
            expected = expected[:-3]
        cmd = [UXF_EXE, name, actual]
        reply = subprocess.call(cmd)
        cmd = ' '.join(cmd)
        if reply != 0:
            print(f'{cmd} • FAIL (execute)')
        else:
            ok += compare(cmd, name, actual, expected, verbose=verbose)
            if not verbose and not ok % 10:
                print('.', end='', flush=True)
    return total, ok


def test_uxf_loads_dumps(uxffiles, total, ok, *, verbose, max_total):
    temp_uxo = uxf.Uxf()
    for name in uxffiles:
        if name.startswith('l'):
            continue # skip linted files that may have changed
        total += 1
        if total > max_total:
            return total - 1, ok
        try:
            with open(name, 'rt', encoding='utf-8') as file:
                uxt = file.read()
        except UnicodeDecodeError:
            with gzip.open(name, 'rt', encoding='utf-8') as file:
                uxt = file.read()
        use_true_false = 'true' in uxt or 'false' in uxt
        try:
            if random.choice((0, 1)):
                uxo = uxf.loads(uxt, verbose=verbose)
            else:
                temp_uxo.loads(uxt, verbose=verbose)
                uxo = temp_uxo
        except uxf.Error as err:
            print(f'loads()/dumps() • {name} FAIL: {err}')
        if random.choice((0, 1)):
            new_uxt = uxo.dumps(use_true_false=use_true_false,
                                verbose=verbose)
        else:
            new_uxt = uxf.dumps(uxo, use_true_false=use_true_false,
                                verbose=verbose)
        nws_uxt = normalize_uxt(uxt)
        nws_new_uxt = normalize_uxt(new_uxt)
        if nws_uxt == nws_new_uxt:
            ok += 1
            if verbose:
                print(f'loads()/dumps() • {name} OK')
            elif not ok % 10:
                print('.', end='', flush=True)
        else:
            print(f'{name} • FAIL (loads()/dumps())')
            if verbose:
                print(f'LOADS = {nws_uxt}\nDUMPS = {nws_new_uxt}')
    return total, ok


def test_uxf_equal(uxffiles, total, ok, *, verbose, max_total):
    for name in uxffiles:
        if name.startswith('l'):
            continue # skip linted files that may have changed
        total += 1
        if total > max_total:
            return total - 1, ok
        try:
            with open(name, 'rt', encoding='utf-8') as file:
                uxt = file.read()
        except UnicodeDecodeError:
            with gzip.open(name, 'rt', encoding='utf-8') as file:
                uxt = file.read()
        try:
            uxo1 = uxf.loads(uxt, verbose=verbose)
        except uxf.Error as err:
            print(f'eq() 1 • {name} FAIL: {err}')
        expected = f'expected/{name}'
        try:
            with open(expected, 'rt', encoding='utf-8') as file:
                uxt = file.read()
        except UnicodeDecodeError:
            with gzip.open(name, 'rt', encoding='utf-8') as file:
                uxt = file.read()
        try:
            uxo2 = uxf.loads(uxt, verbose=verbose)
        except uxf.Error as err:
            print(f'eq() 2 • {expected} FAIL: {err}')
        if eq.eq(uxo1, uxo2):
            ok += 1
            if verbose:
                print(f'eq() • {name} OK')
            elif not ok % 10:
                print('.', end='', flush=True)
        else:
            print(f'{name} • FAIL (eq())')
    return total, ok


def normalize_uxt(text):
    flags = re.DOTALL | re.MULTILINE
    i = text.find('\n') + 1 # ignore header
    body = text[i:]
    comment = ''
    if body.lstrip().startswith('#<'):
        i = body.find('#<')
        if i > -1:
            end = body.find('>')
            if end > -1:
                end += 1
                comment = body[:end].strip()
                body = body[end:].lstrip()
    body = re.sub(r'\d+[Ee]\d+', lambda m: str(float(m.group())), body,
                  flags=flags)
    match = re.match(r'(^=[^[({]+$)*', body, flags=flags)
    if match is not None:
        body = body[match.end():]
        ttypes = sorted(match.group().splitlines())
        body = '\n'.join(ttypes) + '\n' + body
    body = comment + body
    body = ''.join(body.split()) # eliminate whitespace
    return '\n'.join(textwrap.wrap(body, 40)).strip() # easier to compare


def test_uxfconvert(uxffiles, total, ok, *, verbose, max_total):
    N, Y, NF, YR = (0, 1, 2, 3) # No, Yes, No with -f, Yes with -f
    files = [(name, name.replace('.uxf', '.json'), Y) for name in uxffiles]
    files += [(name, name.replace('.uxf', '.xml'), Y) for name in uxffiles]
    files += [('t1.uxf', 't1.csv', N), ('t2.uxf', 't2.csv', N),
              ('0.csv', '0.uxf', N), ('1.csv', '1.uxf', NF),
              ('2.csv', '2.uxf', NF), ('ini.ini', 'ini.uxf', N)]
    for infile, outfile, roundtrip in files:
        if infile.startswith('l'):
            continue # skip linted files that may have changed
        total += 1
        if total > max_total:
            return total - 1, ok
        actual = f'actual/{outfile}'
        cmd = ([UXFCONVERT_EXE, '-f', infile, actual]
               if roundtrip == NF else [UXFCONVERT_EXE, infile, actual])
        reply = subprocess.call(cmd)
        cmd = ' '.join(cmd)
        if reply != 0:
            print(f'{cmd} • FAIL (execute)')
        else:
            expected = f'expected/{outfile}'
            n = compare(cmd, infile, actual, expected, verbose=verbose)
            ok += n
            if not verbose and not ok % 10:
                print('.', end='', flush=True)
            if n:
                if roundtrip in (Y, YR):
                    total += 1
                    new_actual = tempfile.gettempdir() + f'/{infile}'
                    cmd = ([UXFCONVERT_EXE, '-f', expected, new_actual]
                           if roundtrip == YR else
                           [UXFCONVERT_EXE, expected, new_actual])
                    reply = subprocess.call(cmd)
                    cmd = ' '.join(cmd)
                    if reply != 0:
                        print(f'{cmd} • FAIL (execute roundtrip)')
                    else:
                        compare_with = expected
                        i = compare_with.rfind('.')
                        if i > -1:
                            compare_with = compare_with[:i] + '.uxf'
                        if compare(cmd, expected, new_actual, compare_with,
                                   verbose=verbose, roundtrip=True):
                            ok += 1
                            if not verbose and not ok % 10:
                                print('.', end='', flush=True)
                            with contextlib.suppress(FileNotFoundError):
                                os.remove(new_actual)
    total += 1
    actual = 'actual/1-2-csv.uxf'
    infile = '1.csv 2.csv'
    cmd = [UXFCONVERT_EXE, '-f', '1.csv', '2.csv', actual]
    reply = subprocess.call(cmd)
    cmd = ' '.join(cmd)
    if reply != 0:
        print(f'{cmd} • FAIL (execute)')
    else:
        expected = 'expected/1-2-csv.uxf'
        ok += compare(cmd, infile, actual, expected, verbose=verbose)
        if not verbose and not ok % 10:
            print('.', end='', flush=True)
    return total, ok


def test_table_is_scalar(total, ok, *, verbose):
    for (filename, is_scalar) in (('t40.uxf', True), ('t41.uxf', False),
                                  ('t42.uxf', True), ('t43.uxf', False)):
        total += 1
        uxo = uxf.load(filename, verbose=verbose)
        if is_scalar == uxo.data.is_scalar:
            ok += 1
            if verbose:
                print(f'{filename} • (Table.is_scalar) OK')
        else:
            print(f'{filename} • FAIL (Table.is_scalar)')
    return total, ok


def test_slides(slides_py, total, ok, *, verbose):
    num = 1 if slides_py.endswith('1.py') else 2
    cmd = [slides_py, SLIDES_SLD, f'actual/slides{num}']
    total += 1
    reply = subprocess.call(cmd)
    cmd = ' '.join(cmd)
    if reply != 0:
        print(f'{cmd} • FAIL (execute slides)')
    else:
        ok += 1
        for name in sorted(
                name for name in os.listdir(f'actual/slides{num}')
                if name.endswith('.html')):
            total += 1
            ok += compare(cmd, 'slides.sld', f'actual/slides{num}/{name}',
                          f'expected/slides{num}/{name}', verbose=verbose)
    return total, ok


def test_external(cmd, total, ok, *, verbose):
    reply = subprocess.run(cmd, capture_output=True, text=True)
    cmd = ' '.join(cmd)
    if reply.returncode != 0:
        print(f'{cmd} • FAIL')
    else:
        parts = reply.stdout.split()
        try:
            total += int(parts[0].split('=')[1])
            ok += int(parts[1].split('=')[1])
        except (IndexError, ValueError):
            print(f'failed to read total/ok from {cmd}, got {parts!r}')
        if verbose:
            print(f'{cmd} • OK')
    return total, ok


def compare(cmd, infile, actual, expected, *, verbose,
            roundtrip=False):
    try:
        if filecmp.cmp(actual, expected, False):
            if verbose:
                print(f'{cmd} • {infile} → {actual} OK')
            return 1
        elif roundtrip:
            with open(actual, 'rb') as af, open(expected, 'rb') as ef:
                a = af.read()
                i = a.find(b'\n')
                if i > -1:
                    a = a[i:]
                b = ef.read()
                i = b.find(b'\n')
                if i > -1:
                    b = b[i:]
                if a == b:
                    if verbose:
                        print(f'{cmd} • {infile} → {actual} (roundtrip) OK')
                    return 1
        flags = re.DOTALL | re.MULTILINE
        with open(actual, 'rb') as file:
            adata = re.sub(rb'\s+', b'', file.read(), flags=flags)
        with open(expected, 'rb') as file:
            edata = re.sub(rb'\s+', b'', file.read(), flags=flags)
        if adata == edata:
            if infile.endswith('.xml'): # UXF ↔ XML doesn't round-trip
                return 1                # due to ws normalization
            print(
                f'{cmd} • FAIL (compare whitespace) {actual} != {expected}')
        else:
            print(f'{cmd} • FAIL (compare) {actual} != {expected}')
    except FileNotFoundError:
        print(f'{cmd} • FAIL (missing {expected!r})')
    return 0


def cleanup():
    if os.path.exists('actual'):
        shutil.rmtree('actual')
    with contextlib.suppress(FileExistsError):
        os.mkdir('actual')
    with contextlib.suppress(FileExistsError):
        os.mkdir('actual/slides1')
    with contextlib.suppress(FileExistsError):
        os.mkdir('actual/slides2')


def by_number(s):
    match = re.match(r'(?P<name>\D+)(?P<max_total>\d+)', s)
    if match is not None:
        return match['name'], int(match['max_total'])
    return s, 0


if __name__ == '__main__':
    main()
