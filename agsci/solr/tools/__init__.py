from Products.CMFCore.utils import UniqueObject
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Globals import InitializeClass
import Missing
from lxml import etree

try:
    from zope.app.component.hooks import getSite
except ImportError:
    from zope.component.hooks import getSite

class SolrCatalogTool(UniqueObject, SimpleItem):

    id = 'solr_catalog'
    meta_type = 'Solr Catalog Tool'
    
    security = ClassSecurityInfo()

    @property
    def hello(self):
        return "hello"

    def getProperty(self, property_name, default=''):
        site = getSite()

        ptool = getToolByName(site, 'portal_properties')
        props = ptool.get("agsci_solr_properties")

        if props:
            return props.getProperty(property_name, default)
        else:
            return default

    def getSolrURL(self):
        protocol = self.getProperty('solr_protocol', 'http')
        host = self.getProperty('solr_host', '127.0.0.1')
        port = self.getProperty('solr_port', '8080')
        base_url = self.getProperty('solr_base_url', '/solr')        
        
        return "%s://%s:%s%s" % (protocol, host, port, base_url)
        
    
    @property
    def siteId(self):
        site = getSite()
        return site.getId()

    def indexObject(self, context):
        metadata = self.getMetaDataFor(context)
        indexdata = self.getIndexDataFor(context)
        return False
    
    @property
    def portal_catalog(self):
        return getToolByName(getSite(), 'portal_catalog')
    
    def getMetadataFor(self, context):
        m = self.portal_catalog.getMetadataForUID("/".join(context.getPhysicalPath()))
        for k in m.keys():
            if m[k] == Missing.Value:
                m[k] = ''
        return m

    def getIndexDataFor(self, context):
        return self.portal_catalog.getIndexDataForUID("/".join(context.getPhysicalPath()))

    def getCatalogIndexes(self):
        return self.portal_catalog.indexes()

    def getCatalogMetadata(self):
        return self.portal_catalog.schema()   
    
    def exportSchemaXML(self):
        # <schema name="example" version="1.5">
        schema = etree.Element("schema", name="example", version="1.5")

        # Create unique key (UID)
        unique_key = etree.Element('uniqueKey')
        unique_key.text = 'UID'
        schema.append(unique_key)

        # Get indexes and metadata
        indexes = self.getCatalogIndexes()
        metadata = self.getCatalogMetadata()

        # Add a <field> tag for all (most) indexed fields
        fields = list(set(indexes).union(set(metadata)))

        for f in fields:
            p = self.getIndexProperties(f, indexes=indexes, metadata=metadata)

            if not p.get('skip'):
                el = etree.Element("field", 
                                    name=p['name'], type=p['type'], 
                                    indexed=repr(p['indexed']).lower(), stored=repr(p['stored']).lower(), 
                                    multiValued=repr(p['multiValued']).lower(),
                                    required=repr(p['required']).lower()
                                    )
                schema.append(el)

        # Return XML
        return etree.tostring(schema, pretty_print=True, xml_declaration=True, encoding='UTF-8')

    def getIndexProperties(self, index, indexes=[], metadata=[]):

        required = ['getId', 'UID', 'id']

        p = {
                'skip' : False,
                'type' : 'string',
                'name' : index,
                'indexed' : False,
                'stored' : False,
                'multiValued' : False,
                'required' : False,
        }

        i_obj = self.portal_catalog.Indexes.get(index)

        index_config = {
                        'DateIndex' : ('date', False),
                        'FieldIndex' : ('string', False),
                        'ZCTextIndex' : ('text', False),
                        'BooleanIndex' : ('boolean', False),
                        'KeywordIndex' : ('string', True),
                        'UUIDIndex' : ('string', True),
        }

        if index in ('Tags', ):
            import pdb; pdb.set_trace()

        if i_obj:
            (index_type, multiValued) = index_config.get(i_obj.meta_type, (None,False))

            if not index_type:
                p['skip'] = True
            else:
                p['type'] = index_type
                p['multiValued'] = multiValued
                if index in indexes:
                    p['indexed'] = True
                if index in metadata:
                    p['stored'] = True
                if index in required:
                    p['required'] = True
                if hasattr(i_obj, 'indexed_attrs') and i_obj.indexed_attrs:
                    p['name'] = i_obj.indexed_attrs[0]

        return p

InitializeClass(SolrCatalogTool)