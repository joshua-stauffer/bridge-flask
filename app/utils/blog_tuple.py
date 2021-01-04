from collections import namedtuple

BlogResponse = namedtuple(
    typename='BlogResponse', 
    field_names=['content', 'metadata', 'prev_post_id', 'next_post_id'],
    defaults=[None, None, None, None]
)