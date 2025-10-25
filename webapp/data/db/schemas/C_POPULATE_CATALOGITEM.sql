/*  ====================== */
/*  Populate CatalogItem */
/*  ====================== */
/*  This script creates a CatalogItem entry for each artwork from Ipiranga, WikiArt, and SemArt tables.
    The CatalogItem.id will match the source artwork's id for simplicity.
*/

-- Insert CatalogItem entries for all Ipiranga artworks
INSERT INTO CatalogItem (id, ipiranga_id, wikiart_id, semart_id, source)
SELECT 
    id,           
    id,           
    NULL,         
    NULL,         
    'ipiranga'    
FROM Ipiranga
ON DUPLICATE KEY UPDATE 
    ipiranga_id = VALUES(ipiranga_id),
    source = VALUES(source);

-- Insert CatalogItem entries for all WikiArt artworks
INSERT INTO CatalogItem (id, ipiranga_id, wikiart_id, semart_id, source)
SELECT 
    id,         
    NULL,       
    id,         
    NULL,       
    'wikiart'   
FROM WikiArt
ON DUPLICATE KEY UPDATE 
    wikiart_id = VALUES(wikiart_id),
    source = VALUES(source);

-- Insert CatalogItem entries for all SemArt artworks
INSERT INTO CatalogItem (id, ipiranga_id, wikiart_id, semart_id, source)
SELECT 
    id,         
    NULL,       
    NULL,       
    id,         
    'semart'    
FROM SemArt
ON DUPLICATE KEY UPDATE 
    semart_id = VALUES(semart_id),
    source = VALUES(source);

-- Verify the counts
SELECT 
    source,
    COUNT(*) as total_items
FROM CatalogItem
GROUP BY source
ORDER BY source;

-- Show summary statistics
SELECT 
    'Total CatalogItems' as metric,
    COUNT(*) as count
FROM CatalogItem
UNION ALL
SELECT 
    'Ipiranga Items' as metric,
    COUNT(*) as count
FROM CatalogItem WHERE source = 'ipiranga'
UNION ALL
SELECT 
    'WikiArt Items' as metric,
    COUNT(*) as count
FROM CatalogItem WHERE source = 'wikiart'
UNION ALL
SELECT 
    'SemArt Items' as metric,
    COUNT(*) as count
FROM CatalogItem WHERE source = 'semart';
