from eagle import api, fields, models
# import facebook

class FacebookPostsComment(models.Model):
    _name = 'fb.post.comment'
    _rec_name = 'create_by'
    _description = 'Facebook Posts Comment'

    post_id = fields.Many2one(comodel_name="facebook.posts", string="Facebook Post", required=False, )
    create_by_fb_id = fields.Char(string="Create By ID", required=False, )
    create_by = fields.Char(string="Create By", required=False, )
    create_time = fields.Datetime(string="Create At", required=False, )
    comments = fields.Text(string="Comment", required=False, )
    facebook_comment_id = fields.Char(string="Comment FB ID", required=False, )


