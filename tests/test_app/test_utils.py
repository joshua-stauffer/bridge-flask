import unittest
import datetime
from app.utils.blog_tuple import BlogResponse
from app.utils.get_preview_text import get_preview_text
from app.utils.link_check import link_check
from app.utils.prettify_date import prettify_date
from app.utils.to_json import node_to_json, init_Node_dict, add_node, add_link


class UtilsTestCase(unittest.TestCase):

    def test_blog_tuple(self):
        empty_blogresponse = BlogResponse()
        self.assertTrue(empty_blogresponse.content==None)
        self.assertTrue(empty_blogresponse.metadata==None)
        self.assertTrue(empty_blogresponse.prev_post_id==None)
        self.assertTrue(empty_blogresponse.next_post_id==None)
        with self.assertRaises(AttributeError):
            empty_blogresponse.any_other_field
        content = 'hi, some content here'
        metadata = ['a', 'list', 'of', 'something', {'a': 'else'}]
        prev_post_id = 4
        next_post_id = 6
        full_blogresponse = BlogResponse(
            content,
            metadata,
            prev_post_id,
            next_post_id
        )
        self.assertTrue(full_blogresponse.content==content)
        self.assertTrue(full_blogresponse.metadata==metadata)
        self.assertTrue(full_blogresponse.prev_post_id==prev_post_id)
        self.assertTrue(full_blogresponse.next_post_id==next_post_id)


    def test_get_preview_text(self):
        
        # make sure it doesn't throw index error for empty string
        self.assertTrue(get_preview_text('')=='')
        
        # string less than default length? returns string
        short_text = 'hi, a sample short text'
        self.assertTrue(
            get_preview_text(short_text) == short_text
        )
        
        long_text ="""
            Here is a much longer text which will need to be trimmed
            by get_preview_text. Some more text goes here please!
        """ 
        self.assertTrue(len(long_text) > 120)
        # adds an ellipsis to shortened text, so max 123 characters
        self.assertTrue(len(get_preview_text(long_text)) < 123)
        
        # verify that the max_char_count arg works
        self.assertTrue(
            get_preview_text(short_text, 10) == 'hi, a...'
        )

        # verify that if there are spaces or punctuation
        # words aren't being cut in half
        long_word = 'a' * 80
        long_word_text = long_word + ' ' + 'b' * 40
        self.assertTrue(
            get_preview_text(long_word_text) == long_word + '...'
        )
        another_long_word_text = long_word + '.' + 'b' * 40
        self.assertTrue(
            get_preview_text(another_long_word_text) == long_word + '...'
        )

        no_breaks = 'a' * 150
        self.assertTrue(
            get_preview_text(no_breaks) == 'a' * 120 + '...'
        )

    def test_link_check(self):
        self.assertTrue(link_check('No link in this text'))
        self.assertFalse(link_check('There may https://some be a link here'))
        self.assertTrue(link_check("""
            In this text all the false positives appear: 
            http, https, https:, http:
        """))
        self.assertFalse(link_check('but add a backslash and it fails: https:/'))

    def test_prettify_date(self):
        self.assertTrue(prettify_date('') == '')
        self.assertTrue(prettify_date(None) == '')
        self.assertTrue(
            prettify_date(datetime.datetime(2012, 5, 26)) \
                == 'May 26th, 2012'
            )
        self.assertTrue(
            prettify_date(datetime.datetime(2010, 11, 23)) \
                == 'November 23rd, 2010'
            )
        self.assertTrue(
            prettify_date(datetime.datetime(1291, 8, 1)) \
                == 'August 1st, 1291'
            )
        self.assertTrue(
            prettify_date(datetime.datetime(2021, 1, 2)) \
                == 'January 2nd, 2021'
            )
        with self.assertRaises(AttributeError):
            prettify_date('not a datetime object!')

    def test_to_json(self):
        self.assertTrue(
            add_node(1, 'a', 'my label', 5) == {
                'id': 1,
                'group': 'a',
                'label': 'my label',
                'level': 5
            }
        )
        self.assertTrue(
            add_link('some node', 'another node', 4) == {
                'target': 'some node',
                'source': 'another node',
                'strength': 4
            }
        )
        node_dict = init_Node_dict('my title', 1)
        with self.assertRaises(KeyError):
            node_dict['some attribute']
        self.assertTrue(len(node_dict['nodes']) == 3)
        self.assertTrue(len(node_dict['links']) == 2)