# -*- coding: utf-8 -*-

import tempfile
import base64
import os
from PIL import Image

from eagle import models, fields, api
from eagle.exceptions import UserError ,ValidationError

# import facebook
from datetime import datetime



class FacebookPagesConfig(models.Model):
    _name = 'facebook.pages.config'
    _rec_name = 'name'
    _description = 'Facebook Pages'

    name = fields.Char(string="Page Name", required=True, )
    access_token = fields.Char(string="Access Token", required=True, )
    page_id = fields.Char(string="Page ID", required=True, )
    fb_api_version = fields.Char(string="Graph API", default="3.3", required=False, )

    posts_ids = fields.One2many(comodel_name="facebook.posts", inverse_name="page_config_id", string="Posts", required=False, )

    @api.model
    def fetch_all_comment(self):
        for po in self:
            posts__search = self.env['facebook.posts'].search([("page_config_id", "=", po.id)])
            for post in posts__search:
                if not post.state == "removed":
                    FacebookPosts.fetch_comment(post)
                    print(post.title)



class FacebookPosts(models.Model):
    _name = 'facebook.posts'
    _rec_name = "title"
    _description = 'Posts for publish to facebook'

    title = fields.Char(string="Title", required=False, )
    page_config_id = fields.Many2one(comodel_name="facebook.pages.config", string="Pages", required=True, )
    publish_date = fields.Datetime(string="Published On",copy=False )

    message = fields.Text(string="Messege", required=True, )

    on_create_date = fields.Datetime(string="Create On", default=fields.Datetime.now(),copy=False, required=False, )

    facebook_post_id = fields.Char(string="Facebook ID",copy=False, required=False, )

    link = fields.Char(string="Link", required=False, copy=False )

    image = fields.Binary(string="Image", copy=False)

    state = fields.Selection(string="State", selection=[('draft', 'Draft'), ('publish', 'Published'),('removed','Removed') ], default="draft", copy=False ,required=False, )

    comments_ids = fields.One2many(comodel_name="fb.post.comment", inverse_name="post_id", string="Comments", required=False, )
    comment_count = fields.Integer(string="Comment Count", compute="get_comment_count", required=False, )
    like_count = fields.Integer(string="Like Count", required=False, copy=False )

    liked = fields.Boolean(string="Liked",  )
    # def access_token(self):
    #     graph = facebook.GraphAPI(access_token=self.page_config_id.access_token,
    #                               version=self.page_config_id.fb_api_version)
    #     return graph

    _sql_constraints = [
        ('unique_facebook_id','unique(facebook_post_id)',"Facebook Must be Unique!")
    ]

    def graph_api(self ):
        try:
            graph = facebook.GraphAPI(access_token=self.page_config_id.access_token, version=self.page_config_id.fb_api_version)
        except facebook.GraphAPIError as e:
            print(e.message)
        return graph


    def put_like_for_this_post(self):
        all_likes = self.graph_api().get_object(id=self.facebook_post_id, fields="likes{id}")
        print(all_likes)
        if not self.page_config_id.page_id == all_likes["id"]:
            # self.graph_api().put_like(object_id=self.facebook_post_id)
            print("not liked")

    def get_likes(self):
        post_like = self.graph_api().get_object(id=self.facebook_post_id, fields="likes{id,name}")
        like_data = post_like["likes"]["data"]
        self.like_count = len(like_data)
        print(like_data,len(like_data))

    @api.multi
    def open_image(self):
        self.ensure_one()
        if not self.image:
            raise UserError("no image on this record")
        # decode the base64 encoded data
        data = base64.decodebytes(self.image)

        print(data)
        print(self.image)
        # create a temporary file, and save the image
        fobj = tempfile.NamedTemporaryFile(delete=False)
        fname = fobj.name
        fobj.write(data)
        fobj.close()
        print(fname)
        # # open the image with PIL
        try:
            image = Image.open(fname)
            print(image)
        #     # do stuff here
        finally:
            # delete the file when done
            os.unlink(fname)


    def publish_post_facebook(self):
        if self.state == "publish":
            post = self.env["facebook.posts"]
            print(post)

        else:
            self.graph_api().put_object(parent_object=self.page_config_id.page_id, connection_name="feed", message=self.message, link=self.link or None)
            post = self.graph_api().get_object(id=self.page_config_id.page_id, fields="posts{id,created_time}")
            # profile = graph.get_object(id ="me", fields="id,name,email")
            # for id in post['posts']

            post_ids_list = post['posts']['data']
            self.facebook_post_id = post_ids_list[0]['id']

            self.publish_date = datetime.now()
            print(self.publish_date)

            # print(datetime.strptime(post_ids_list[0]['created_time'], "%m %d %Y $H:%M:%S"))

            print(self.facebook_post_id)

            self.state = "publish"



    def test_date(self):
        time_r = "2019-06-19T07:49:40+0000".replace("T", " ")
        print(datetime.strptime(time_r, "%Y-%m-%d %H:%M:%S%z"))

        print(self.image)
        # print(datetime.strptime(post_ids_list[0]['created_time'], "%m %d %Y $H:%M:%S"))



    def fetch_comment(self):
        for comment in self:
            posts_comment = comment.graph_api().get_object(id=comment.facebook_post_id, fields="comments")
            fb_comment = self.env['fb.post.comment']
            # comment_data = posts_comment['comments']
            if "comments" in posts_comment:
                comment_data = posts_comment['comments']['data']
                for msg in comment_data:
                    if not  comment.comments_ids.filtered(lambda f: f.facebook_comment_id == msg['id']):
                        fb_comment.create({
                            'post_id'           : comment.id,
                            'create_by_fb_id'   : msg['from']['id'],
                            "create_by"         : msg['from']['name'],
                            "create_time"       : msg['created_time'],
                            "comments"          : msg['message'],
                            "facebook_comment_id" : msg['id'],
                        })
                    else:
                        pass
                        # raise ValidationError("This is Not Found a new Comment just mow!")

                print(comment_data,len(comment_data),comment.comment_count)
            else:
                raise ValidationError("This is Not Found Comment just mow!")



    @api.depends("comments_ids")
    def get_comment_count(self):
        for comment in self:
            comment.comment_count = len(comment.comments_ids)



    def delete_facebook_post(self):
        self.graph_api().delete_object(id=self.facebook_post_id)
        self.state = "removed"


    # print(comment_data,len(comment_data))
    # return len(comment_data)
#
# class DeleteFacebookPost(models.TransientModel):
#     _name = 'delete.facebook.post'
#     _description = 'Delete Posts from Facebook'
#
#
#
#     def delete_facebook_post(self):
#         context = dict(self._context or {})
#         active_id = context.get('active_ids', []) or []
#
#         FacebookPosts.graph_api(self).delete_object(id=self.facebook_post_id)
#         self.state = "removed"






        # {'posts': {'paging': {'cursors': {
        #                 'before': 'Q2c4U1pXNTBYM0YxWlhKNVgzTjBiM0o1WDJsa',
        #                 'after': 'Q2c4U1pXNTBYM0YxWlhKNVgzTjBiM0o1WDJsa0'}},
        #
        #            'data': [{'id': '621082501727675_622063364962922'}, {'id': '621082501727675_622061158296476'},
        #                     {'id': '621082501727675_622053344963924'}, {'id': '621082501727675_622048801631045'},
        #                     {'id': '621082501727675_621908841645041'}, {'id': '621082501727675_621908354978423'},
        #                     {'id': '621082501727675_621906311645294'}, {'id': '621082501727675_621904528312139'},
        #                     {'id': '621082501727675_621886471647278'}, {'id': '621082501727675_621885351647390'}]},
        #  'id': '621082501727675'}
