import gbdtransformation.brands.ipas.filters as ipas

ignore_namespace = [
   'http://www.wipo.int/standards/XMLSchema/trademarks',
   'http://www.wipo.int/standards/XMLSchema/wo-trademarks']

def get_appdate(appdate, appnum):
    return appnum.split('/')[-2].zfill(4)

def translate_type(header):
    code = header.TransactionCode
    subcode = header.TransactionSubCode

    if subcode == 'Denominación de Origen': return 'AO'
    if subcode == 'Indicación Geógrafica': return 'AO'

    if code == 'Trademark': return 'TRADEMARK'
    if code == 'Registro de Marca': return 'TRADEMARK'
    if code == 'Renovación de Marca': return 'TRADEMARK'

    raise Exception('Type "%s" is not mapped.' % code)

def translate_kind(trademark, header):
    subcode = header.TransactionSubCode

    if not subcode:
        return ['Undefined']

    if subcode == 'Part A': return ['Individual']
    if subcode == 'Part B': return ['Individual']
    if subcode == 'National': return ['Individual']

    if subcode == 'Marca de Producto': return ['Individual']
    if subcode == 'Marca de Servicios': return ['Individual']
    if subcode == 'Marca de Servicio (Ren.)': return ['Individual']
    if subcode == 'Marca de Producto (Ren.)': return ['Individual']

    if subcode == 'Denominación de Origen': return ['Other']
    if subcode == 'Indicación Geógrafica': return ['Other']

    return ['Other']
    #raise Exception('Kind "%s" not mapped.' % subcode)

def translate_status(trademark):
    status = trademark.MarkCurrentStatusCode

    if status == 'TM Applications Received in Error': return 'Ended'

    return ipas.translate_status(status)

def translate_feature(trademark):
    feature = trademark.MarkFeature

    if not feature: return 'Undefined'

    if feature == 'Denominativa': 
        return 'Word'

    if feature == "Mixta": 
        return 'Combined'

    if feature == "Figurativa": 
        return "Figurative"

    if feature == "Tridimensional":
        return 'Three dimensional';

    if feature == 'Olfativa':
        return 'Olfactory';

    if feature == "Sonora": 
        return "Sound"    
    #else:
    #   raise Exception('feature "%s" not mapped.' % feature) 
    
    return ipas.translate_feature(feature)

def verbal_lang_map(markVerbalElements, applang=None):
    return ipas.verbal_lang_map(markVerbalElements, applang=applang)

def translate_event(event):
    if event == 'TM Applications Received in Error': return 'Withdrawn'
    return ipas.translate_event(event)

def get_registration_nb(trademark, tmstatus):
    if trademark.RegistrationNumber:
        return trademark.RegistrationNumber

    if not tmstatus in ['Expired', 'Registered']:
        return None

    # PG/M/1/062947 => 1/062947
    appnum_parts = trademark.ApplicationNumber.split('/')
    regnum = '%s/%s' % (appnum_parts[-2], appnum_parts[-1])
    return regnum

def get_expiry_date(trademark, tmstatus):
    return ipas.get_expiry_date(trademark, tmstatus)

def get_registration_date(trademark, tmstatus):
    return ipas.get_registration_date(trademark, tmstatus)

# no international for PG
def is_international(header):
    return False

# never accessed
def get_ir_refnum(appnum):
    return

def get_goods_services(goods_services):
    return ipas.get_goods_services(goods_services)

def image_filename_extension(filename, extension_element):
    if extension_element:
        return filename + "." + extension_element.lower()
    else:
        return filename

def get_publication_date(publications):
    # in the publication information, in case:
    # PublicationSection == "Registration"
    # the associated PublicationDate is the publicationDate
    if publications == None:
        return None
    if isinstance(publications, list):
        for publication in publications:
            if 'PublicationSection' in publication and publication['PublicationSection'] == 'Registration':
                if 'PublicationDate' in publication:
                    return publication['PublicationDate']
    else:
        if "Publication" in publications:
            publication = publications["Publication"]
            if 'PublicationDate' in publication:
                return publication['PublicationDate']
    return None
