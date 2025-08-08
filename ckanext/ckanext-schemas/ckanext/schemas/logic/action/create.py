import ckan.plugins.toolkit as toolkit
import ckanext.schemas.utils as utils
from ckan.logic.action.create import package_create as ckan_package_create

@toolkit.chained_action
def package_create(original_action, context, data_dict):
    """
    Custom package_create that computes and saves clusters field
    """
    # Compute clusters before saving
    vocab_clusters = utils.relevant_clusters(data_dict)
    
    # Add clusters to the data being saved
    if vocab_clusters:
        data_dict['clusters'] = vocab_clusters
    
    # Call the default package_create
    result = original_action(context, data_dict)
    
    return result