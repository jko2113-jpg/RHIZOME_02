#!/usr/bin/env python3
"""Convert LIST.csv to clean CSV and network.json for RHIZOME_02."""
import csv
import json
import re
from collections import Counter

CATEGORY_MAP = {
    'ARCHIVE': 'Archive', 'ARCHIVE ': 'Archive', 'ARCHIVE/BOOKSTORE': 'Archive',
    'ARTIFACT': 'Artifact',
    'BLOG': 'Blog',
    'BOOK': 'Book', 'BOOKS': 'Book',
    'BOOKSTORE': 'Bookstore', 'BOOKSTORE/RECORDS': 'Bookstore',
    'DATA': 'Data',
    'DATABANK': 'Reference', 'DATABANK ': 'Reference',
    'DOCUMENTARY': 'Film', 'DOCUMENTARY/ARCHIVE': 'Film',
    'ENCYCLOPEDIA': 'Reference',
    'ENTITY': 'Practice', 'PRACTICE': 'Practice',
    'ENTORAGE': 'Entourage', 'ENTOURAGE': 'Entourage',
    'FILM': 'Film', 'FILM ARCHIVE': 'Film',
    'GUIDE': 'Guide', 'HOW TO / GUIDE': 'Guide',
    'INSTITUTION': 'Institution',
    'LECTURE': 'Film',
    'MAPPING': 'Mapping',
    'MATERIALS': 'Materials', 'MATERIALS / STORE': 'Materials',
    'MODEL MAKING': 'Guide',
    'PLUG IN': 'Software', 'SOFTWARE': 'Software',
    'PUBLICATION': 'Publication', 'Publication': 'Publication',
    'REFERENCE': 'Reference', 'REFERENCE ': 'Reference',
    'SOUND': 'Sound',
    'TOOL': 'Tool',
    'WEBSITE': 'Reference',
}

MANUAL_CATS = {
    'angelosays': 'Blog', 'cornell intypes': 'Reference',
    'cronologia': 'Reference', 'hatch maker': 'Software',
    'ejnyc': 'Mapping', 'schwarz triangle': 'Reference',
    'nlab': 'Reference', 'quasiisothermic': 'Reference',
    'berlage': 'Institution', 'tripyramid': 'Practice',
    'g.lab': 'Blog', 'media-n': 'Publication',
    'laboratory for the physics': 'Institution',
    'cabinet': 'Publication', 'graham foundation': 'Institution',
    'greg lynn': 'Practice', 'lom': 'Materials',
    'sonorous objects': 'Materials', 'clippy': 'Materials',
    'hans hollein': 'Publication', 'architecture off-cent': 'Publication',
    'baldwin effect': 'Reference', 'geometric graph': 'Reference',
    'words are at sea': 'Blog', 'cantor': 'Reference',
    'euler math': 'Reference', 'bar-natan': 'Reference',
    'drawing matter': 'Archive', 'lancaster': 'Archive',
    'acoustic ornament': 'Reference', 'architectural acoustics': 'Book',
    'novelty of symmetry': 'Reference', 'basilisk': 'Reference',
    'un-private house': 'Archive', 'shoei yoh': 'Practice',
    'axonometrica': 'Blog', 'control syntax rio': 'Archive',
    'pedagogical sketchbook': 'Book', 'pedogogical': 'Book',
    'floating house': 'Practice', 'libeskind': 'Practice',
    'boxmorphobject': 'Guide', 'new massings': 'Book',
    'interference phenomena': 'Reference', 'new italian blood': 'Archive',
    'shinkenchiku': 'Archive', 'strange weather': 'Reference',
    'contemporary art library': 'Archive', 'mit act': 'Institution',
    'polyagogy': 'Reference', 'archaeoacoustics': 'Sound',
    'ccrma': 'Sound', 'nagata': 'Sound',
    'gerhard richter': 'Archive', 'vincent borrelli': 'Bookstore',
    'spherical mic': 'Sound', 'makerspace': 'Institution',
    '24/7': 'Book', 'architekturmuseum': 'Institution',
    'vincent de rijk': 'Practice', 'visible weather': 'Reference',
    'topological data': 'Reference', 'cesium': 'Mapping',
    'avogadro': 'Software', 'hiromi fujii': 'Archive',
    'scott cohen': 'Practice', 'arducam': 'Reference',
    'ri filter': 'Reference', 'short account of the eye': 'Book',
    'dayton audio': 'Materials', 'dfr': 'Archive',
    'danteum': 'Reference', 'dibujos ejemplares': 'Reference',
    'map2model': 'Tool', 'dml speaker': 'Reference',
    'teaching systems': 'Reference', 'quadralectic': 'Reference',
    'arca': 'Publication', 'transmaterial': 'Book',
    'van doesburg': 'Reference', 'columbia-princeton': 'Sound',
    'archipel': 'Archive', 'afasia': 'Archive',
    'kirkegaard': 'Bookstore', 'window research': 'Institution',
    'twentieth century engineering': 'Book',
    'nina katchadourian': 'Archive', 'episteme': 'Reference',
    'spectres of the state': 'Archive', 'kim swoo geun': 'Archive',
    'tokyo arts': 'Institution', 'mmca': 'Institution',
    'future materials': 'Materials', 'shin sangho': 'Archive',
    'veldwerk': 'Practice', 'wai': 'Publication',
    'interchronic': 'Archive', 'mapping gothic': 'Mapping',
    'howard carter': 'Archive', 'architectural media': 'Archive',
    'epfl': 'Reference', 'equivalent exchange': 'Reference',
    'library project': 'Archive', 'john barr': 'Practice',
    'burning farm': 'Practice', 'every building': 'Mapping',
    'pepakura': 'Software', 'form finding lab': 'Institution',
    'studio folder': 'Practice', 'lacan': 'Reference',
    'nameless': 'Practice', 'post model medium': 'Reference',
    'davidneat': 'Guide', 'optical flow': 'Reference',
    'ofhouses': 'Archive',
}

CATEGORY_TAGS = {
    'Archive': ['archive'], 'Artifact': ['artifact'],
    'Blog': ['blog'], 'Book': ['book', 'pdf', 'reading'],
    'Bookstore': ['bookstore', 'nyc'], 'Data': ['live-data', 'real-time'],
    'Entourage': ['3d', 'entourage'], 'Film': ['film', 'video'],
    'Guide': ['tutorial', 'guide'], 'Institution': ['institution'],
    'Mapping': ['mapping', 'gis'], 'Materials': ['materials'],
    'Practice': ['practice', 'architecture'], 'Publication': ['publication'],
    'Reference': ['reference'], 'Software': ['software'],
    'Sound': ['sound', 'acoustics'], 'Tool': ['tool'],
    'Uncategorized': [],
}

KEYWORD_TAGS = [
    ('instagram', 'social-media'), ('rhino', 'rhino'),
    ('grasshopper', 'parametric'), ('drawing', 'drawing'),
    ('architecture', 'architecture'), ('nyc', 'nyc'),
    ('new york', 'nyc'), ('acoustic', 'acoustics'),
    ('sound', 'sound'), ('music', 'music'),
    ('math', 'mathematics'), ('geometr', 'geometry'),
    ('material', 'materials'), ('glass', 'glass'),
    ('free', 'open-access'), ('open access', 'open-access'),
    ('feminist', 'feminist'), ('color', 'color'),
    ('colour', 'color'), ('typography', 'typography'),
    ('font', 'typography'), ('struct', 'structures'),
    ('fabricat', 'fabrication'), ('3d', '3d'),
    ('pdf', 'pdf'), ('inflat', 'inflatables'),
    ('optic', 'optics'), ('texture', 'texture'),
    ('render', 'rendering'), ('digital', 'digital'),
    ('map', 'mapping'), ('graph', 'geometry'),
]


def normalize_category(raw, name):
    normalized = CATEGORY_MAP.get((raw or '').strip())
    if normalized:
        return normalized
    name_l = name.lower()
    for key, cat in MANUAL_CATS.items():
        if key in name_l:
            return cat
    return 'Uncategorized'


def make_tags(name, category, description, url=''):
    tags = set(CATEGORY_TAGS.get(category, []))
    text = (name + ' ' + (description or '') + ' ' + (url or '')).lower()
    for keyword, tag in KEYWORD_TAGS:
        if keyword in text:
            tags.add(tag)
    return sorted(list(tags))[:8]


def clean_url(raw):
    if not raw:
        return None
    s = raw.strip()
    if 'chrome-extension://' in s:
        m = re.search(r'https?://\S+', s)
        return m.group(0).rstrip() if m else None
    if s.startswith('http'):
        return s.rstrip()
    return None


PHYSICAL_RE = re.compile(
    r'^\d+\s+\w.*(?:Ave|St|Street|Road|Blvd|Broadway|Way)',
    re.IGNORECASE
)


def is_physical(s):
    return bool(PHYSICAL_RE.match(s.strip())) if s else False


def make_id(name, url=''):
    base = (name or url or '').lower().strip()
    base = re.sub(r'[^\w\s-]', '', base)
    base = re.sub(r'\s+', '-', base)
    base = re.sub(r'-+', '-', base).strip('-')
    return base[:40]


def process(csv_path, old_json_path):
    # Preserve existing hand-curated connections
    old_connections = {}
    try:
        with open(old_json_path) as f:
            for item in json.load(f):
                if item.get('url') and item.get('connections'):
                    old_connections[item['url']] = item['connections']
    except Exception:
        pass

    nodes = []
    seen_urls = {}

    with open(csv_path, encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            if not any(row):
                continue
            while len(row) < 17:
                row.append('')

            name        = row[0].strip()
            cat_raw     = row[1].strip()
            description = row[2].strip()
            location    = row[3].strip()

            extra_urls = [u for cell in row[4:] if (u := clean_url(cell.strip()))]

            url      = clean_url(location)
            physical = location if (not url and is_physical(location)) else None

            if not name and not url and not physical:
                continue

            # Dedup: merge extras into existing node
            if url and url in seen_urls:
                idx = seen_urls[url]
                for eu in extra_urls:
                    if eu not in nodes[idx]['connections']:
                        nodes[idx]['connections'].append(eu)
                continue

            category    = normalize_category(cat_raw, name)
            tags        = make_tags(name, category, description, url or '')
            node_id     = make_id(name, url or '')
            connections = list(old_connections.get(url or '', []))
            for eu in extra_urls:
                if eu not in connections:
                    connections.append(eu)

            node = {
                'id':          node_id,
                'url':         url or physical or '',
                'title':       name,
                'description': description,
                'category':    category,
                'tags':        tags,
                'connections': connections,
            }
            if url:
                seen_urls[url] = len(nodes)
            nodes.append(node)

    return nodes


def write_csv(nodes, path):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['id', 'url', 'title', 'description',
                                          'category', 'tags', 'connections'])
        w.writeheader()
        for n in nodes:
            w.writerow({
                'id':          n['id'],
                'url':         n['url'],
                'title':       n['title'],
                'description': n['description'],
                'category':    n['category'],
                'tags':        '|'.join(n['tags']),
                'connections': '|'.join(n['connections']),
            })


def write_json(nodes, path):
    out = [
        {'url': n['url'], 'title': n['title'], 'description': n['description'],
         'category': n['category'], 'tags': n['tags'], 'connections': n['connections']}
        for n in nodes if n['url']
    ]
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    return out


if __name__ == '__main__':
    BASE = '/home/user/RHIZOME_02'
    nodes = process(f'{BASE}/LIST.csv', f'{BASE}/network.json')
    write_csv(nodes, f'{BASE}/LIST_clean.csv')
    out = write_json(nodes, f'{BASE}/network.json')

    cats = Counter(n['category'] for n in nodes)
    print(f"Total nodes: {len(nodes)}")
    print("\nCategory breakdown:")
    for cat, count in sorted(cats.items()):
        print(f"  {cat:25s}: {count}")
    print(f"\nWrote LIST_clean.csv and network.json")
