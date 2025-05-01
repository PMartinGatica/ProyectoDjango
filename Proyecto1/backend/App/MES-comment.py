# Las librerías se importan desde el script Padre
test_file = tmp_directory / "TestCodes.pkl"

codes = sorted(pd.read_pickle(test_file).iloc[:, 0].tolist(), key=len, reverse=True)

patterns = {
    'track_id': re.compile(r'[Zz][A-Za-z0-9](?=.*[2-9])[B-DF-HJ-NP-TV-Zb-df-hj-np-tv-z2-9]{8}'),
    'url': re.compile(r'http\S+\.\S+\b'),
    'codigo_8s': re.compile(r'8S{1,2}%?[A-Za-z0-9%\'-]{6,}\b', re.IGNORECASE),
    'TM': re.compile(r'\bt[\s.,/:-]*m\b|\bt[\s.,/:-]*mañana\b', re.IGNORECASE),
    'TT': re.compile(r'\bt[\s.,/:-]*t\b|\bt[\s.,/:-]*tarde\b', re.IGNORECASE),
    'TN': re.compile(r'\bt[\s.,/:-]*n\b|\bt[\s.,/:-]*noche\b', re.IGNORECASE),
    'HHEE': re.compile(r'\bh(?:[.,\s/-])*e(?:[.,\s/-])*e\b|\bhora(?:s)?(?:\s)*extra(?:s)?\b', re.IGNORECASE),
    'reparado_turno': re.compile(r'\b(?:Rep|\w*arado)\s+en\s+(t[\s.,/:-]*(m|t|n|mañana|tarde|noche))\b', re.IGNORECASE),
    'Acum': re.compile(r'(\baucm|aacum\w*|acum\w*)\b', re.IGNORECASE),
    'B2F': re.compile(r'(b2f|backflash|bf2)', re.IGNORECASE),
    'Scrap': re.compile(r'\b(scrap|escrap)\b', re.IGNORECASE),
    'Tcode': re.compile(r'\b(?!.*(?:reporte|estetico|enciende|casos|origen|proceso|faltante|rma|zocalo|wuhan))(?:[A-Z0-9]+(?:_[A-Z0-9]+)*_?(?:\(dBm\))?(?:_(?:2\.4G(?:Hz)?|5\.0G(?:Hz)?|USB-[A-Z0-9]))?(?:_[A-Z0-9]+)*_[A-Z0-9]+(?:\.\d{2})?)\b', re.IGNORECASE)
}

def limpieza_primaria(comment):  # Ahora recibe una cadena, no un DataFrame
    if pd.isna(comment): return None
    comment = str(comment)  # Asegurar que sea una cadena
    comment = re.sub(r'\t+', ' ', comment) \
        .replace('´', '') \
        .translate(str.maketrans('áéíóúÁÉÍÓÚ', 'aeiouAEIOU'))
    comment = re.sub(r'\[(?!.*\])|\](?!.*\[)', '', comment)
    comment = re.sub(r'(?<!\d);(?![\s\d])', '', comment)
    return comment.strip()  # Eliminar espacios en blanco al inicio/final

def limpieza_adicional(text):
    if pd.isna(text): return text  # Verificar si el texto es NaN
    text = str(text)  # Convertir a string para procesarlo
    text = re.compile(r'([^A-Za-z0-9_\s])(?:\s*\1)+').sub(lambda m: m.group(1), text) # Reemplazar múltiples caracteres especiales consecutivos con uno solo
    apertura = r'¿¡\(\{\[\<«“‘' # Lista de signos de apertura
    text = re.sub(r'([' + apertura + r'])\s+', r'\1', text) # Quitar espacios después de los signos de apertura
    text = re.sub(r'\s*([' + apertura + r'])', r' \1', text) # Asegurar un espacio antes de los signos de apertura
    otros = r"""!"#$%&'*)+,-./:;=?@[\]^{|}~""" # Lista de otros signos de puntuación a ajustar
    text = re.sub(r'\s+([' + re.escape(otros) + r'])', r'\1', text) # Quitar espacios antes de los signos de puntuación
    text = re.sub(r'([' + re.escape(otros) + r'])(?!\s|$)', r'\1 ', text) # Asegurar un espacio después de los signos de puntuación
    if not re.search(r'[A-Za-z0-9]', text): return '-'
    text = re.sub(r'\(\)|\[\]', '', text)
    text = re.sub(r'^[^A-Za-z0-9\(\[]+|[^A-Za-z0-9\)\]]+$', '', text)
    return re.sub(r'\s{2,}', ' ', text).strip() # Reemplazar múltiples espacios consecutivos por uno solo y eliminar espacios extremos

def clean_comment(comment):
    if pd.isna(comment): return None, None, None, None, comment, None
    comment = str(comment)

    comment = limpieza_primaria(comment)

    # URL
    urls = ' | '.join(patterns['url'].findall(comment)) or None
    comment = patterns['url'].sub('', comment).strip()
    
    # 8S
    cod8s = ' | '.join(patterns['codigo_8s'].findall(comment)).replace("'", "-") or None
    comment = patterns['codigo_8s'].sub('', comment).strip()

    # TrackID
    matches = patterns['track_id'].findall(comment)
    if matches:
        unique_tracks = list(set(matches))  # Obtener únicos
        extracted_track = ' '.join(unique_tracks)  # Unir los únicos en una cadena
        if len(unique_tracks) == 1:  # Si todos los encontrados son iguales
            match = unique_tracks[0]
            if re.fullmatch(r'(' + re.escape(match) + r'\s*)+', comment): # Verificar si el comentario contiene solo duplicados del mismo track_id
                comment = ''  # Eliminar todo el comentario
            else: # Eliminar todas las apariciones del track_id único
                comment = re.sub(r'\b' + re.escape(match) + r'\b', '', comment).strip()
    else:
        extracted_track = None

    # TESTCODE
    found_testcodes = []
    for code in codes:
        if code in comment:
            found_testcodes.append(code)
            comment = comment.replace(code, '', 1).strip()
    extracted_testcodes = ' | '.join(found_testcodes) if found_testcodes else None
    if found_testcodes:
        if len(found_testcodes) == 1 and "pdf" not in comment.lower():
            code = found_testcodes[0]
            comment = comment.replace(code, '').strip()
        else:
            pass  # Do not remove from comment if more than one

    # Otros TestCodes
    if "pdf" not in comment.lower():  # Verificar si "pdf" no está presente en el comentario
        other_testcodes = patterns['Tcode'].findall(comment)  # Buscar con regex 'Tcode'
        if other_testcodes:
            other_testcodes = [code for code in other_testcodes if len(code) >= 30]
            if other_testcodes:
                extracted_other_testcodes = ' / '.join(other_testcodes)  # Unir en una cadena
                comment = patterns['Tcode'].sub('', comment).strip()  # Eliminar las coincidencias del comentario
            else:
                extracted_other_testcodes = None
        else:
            extracted_other_testcodes = None
    else:
        extracted_other_testcodes = None  # Si contiene "pdf", no extraer TestCodes

    # une testcodes y limpia
    combined_testcodes = ' / '.join(filter(None, [extracted_testcodes, extracted_other_testcodes])) if extracted_testcodes or extracted_other_testcodes else None
    comment = limpieza_adicional(comment) # LIMPIEZA ADICIONAL

    # Detalle
    detalles = []
    for key, replacement in [('Acum', 'Acum'), ('B2F', 'B2F'), ('Scrap', 'Scrap')]:
        matches = patterns[key].findall(comment)
        if matches:
            detalles.append(replacement)  # Agregar el término estándar al Detalle
            comment = patterns[key].sub(replacement, comment).strip()  # Sustituir por el término estándar en COMENTARIO
        if key == 'Acum':  # Eliminar solo 'Acum' del comentario
            comment = comment.replace(replacement, '').strip()
    detalle = ' '.join(detalles) if detalles else None

    # TURNOS
    comment = patterns['reparado_turno'].sub('', comment).strip() # Remove "Reparado en <turno>"
    extracted_turnos = []
    for turno_key in ['TM', 'TT', 'TN', 'HHEE']:
        matches = patterns[turno_key].findall(comment)
        if matches:
            extracted_turnos.extend([turno_key.upper()] * len(matches))
            if turno_key == 'HHEE' and len(matches) == 1:
                comment = patterns[turno_key].sub('', comment).strip()
    turnos_unique = list(dict.fromkeys(extracted_turnos)) # Eliminar duplicados manteniendo el orden

    # Si hay más de un turno único (TM, TT, TN), no eliminar turnos del comentario
    turnos_set = set(turnos_unique).intersection({'TM', 'TT', 'TN'})
    if len(turnos_set) > 1:
        pass  # No eliminar turnos si hay más de uno
    else:
        for turno_key in ['TM', 'TT', 'TN']:  # Si hay un solo turno (o repetidos del mismo tipo), eliminarlos del comentario
            comment = patterns[turno_key].sub('', comment).strip()

    turno = ' '.join(turnos_unique) if turnos_unique else None     # Unir los turnos únicos en una cadena

    comment = limpieza_adicional(comment) # LIMPIEZA ADICIONAL

    return extracted_track, urls, cod8s, combined_testcodes, comment, turno, detalle

