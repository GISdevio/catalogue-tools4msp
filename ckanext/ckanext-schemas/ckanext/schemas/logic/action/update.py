import ckan.plugins.toolkit as toolkit
import ckanext.schemas.utils as utils
from ckan.logic.action.update import package_update as ckan_package_update

@toolkit.chained_action
def package_update(original_action, context, data_dict):
    """
    Custom package_update that computes and saves vocab_clusters field
    """
    # Compute vocab_clusters before saving
    vocab_clusters = utils.relevant_clusters(data_dict)
    
    # Add vocab_clusters to the data being saved
    if vocab_clusters:
        data_dict['clusters'] = vocab_clusters
    
    # Call the default package_update
    result = original_action(context, data_dict)
    
    return result