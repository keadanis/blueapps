# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import http
from odoo.http import request, Response
from datetime import datetime
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website_slides.controllers.main import WebsiteSlides


class WebsiteSlidesORA(WebsiteSlides):

    @http.route('/ora/response/save/', type='http', auth="user", website=True)
    def save_response(self, **kwargs):
        user_response = self._get_access_data(kwargs)
        slide = request.env['slide.slide'].sudo().browse(int(kwargs.get('slide_id')))
        if kwargs.get('submit') == 'save':
            self.add_answers(kwargs, user_response)
        if kwargs.get('submit') == 'resubmit_fresh':
            self._get_access_data(kwargs, resubmit=True)
            user_response.state = 'inactive'
        if kwargs.get('submit') == 'resubmit_copy':
            resubmit_copy_response = self._get_access_data(kwargs, resubmit=True)
            self.add_answers(kwargs, resubmit_copy_response)
            user_response.state = 'inactive'
        if kwargs.get('submit') == 'submit':
            user_response.state = 'submitted'
            user_response.submitted_date = datetime.now()
            self.add_answers(kwargs, user_response)
            if slide.peer_assessment:
                peer_limit = slide.peer_limit
                enrolled_users = slide.channel_id.partner_ids.filtered(lambda l: l.id != request.env.user.partner_id.id)
                if peer_limit <= len(enrolled_users):
                    peer_limit = peer_limit
                else:
                    peer_limit = len(enrolled_users)
                for _ in range(peer_limit):
                    peer_user = slide._get_peer_user(user_response)
                    if peer_user:
                        request.env['open.response.rubric.staff'].create({
                            'assess_type': 'peer',
                            'user_id': peer_user.id,
                            'state': 'in_progress',
                            'response_id': user_response.id
                        })
            user_response.message_post(
                body='This response has been submitted!', message_type='notification',
                subtype_xmlid='mail.mt_comment', author_id=request.env.user.partner_id.id,
                partner_ids=[user_response.staff_id.partner_id.id])
        return request.redirect('/slides/slide/%s' % slug(slide))

    def _get_access_data(self, post, resubmit=False):
        user = request.env.user
        slide_id = request.env['slide.slide'].sudo().browse(int(post.get('slide_id')))
        if slide_id.response_ids and not resubmit:
            response = slide_id.response_ids.filtered(lambda x: x.state in ['active', 'submitted'] and x.user_id == user)
            if response:
                return response
        response = slide_id._create_answer(request.env.user.id)
        return response

    def add_answers(self, kwargs, response):
        if kwargs.get('response_id'):
            old_user_response = request.env['ora.response'].browse(int(kwargs.get('response_id')))
            for line in response.user_response_line:
                for oline in old_user_response.user_response_line:
                    if line.prompt_id == oline.prompt_id:
                        if line.response_type == 'text':
                            line.value_text_box = oline.value_text_box
                        elif line.response_type == 'rich_text':
                            query = ("update open_response_user_line set value_richtext_box='%s' where id=%s") % (oline.value_richtext_box, oline.id)
                            request.cr.execute(query)
        else:
            for line in response.user_response_line:
                if line.response_type == 'text':
                    line.value_text_box = kwargs[str(line.prompt_id.id)]
                elif line.response_type == 'rich_text':
                    query = ("update open_response_user_line set value_richtext_box='%s' where id='%s'") % (kwargs[str(line.prompt_id.id)], line.id)
                    request.cr.execute(query)

    def _prepare_additional_channel_values(self, values, **kwargs):
        values = super(WebsiteSlidesORA, self)._prepare_additional_channel_values(values, **kwargs)
        slide = values.get('slide')
        submitted = False
        if slide and slide.prompt_ids:
            values.update({
                'slide_prompts': [{
                    'id': prompt.id,
                    'sequence': prompt.sequence,
                    'question': prompt.question_name,
                    'response_type': prompt.response_type,
                    'submitted': submitted,
                    'name': prompt.name,
                } for prompt in slide.prompt_ids.sorted(key=lambda x: x.id)]
            })
        if slide and slide.response_ids:
            total_responses = slide.response_ids.filtered(lambda l: l.user_id == request.env.user)
            submitted_response = total_responses.filtered(lambda l: l.state == 'submitted')
            active_response = total_responses.filtered(lambda l: l.state == 'active')
            inactive_response = total_responses.filtered(lambda l: l.state == 'inactive')
            assessed_response = total_responses.filtered(lambda l: l.state == 'assessed')
            values['submitted_response'] = submitted_response
            values['active_response'] = active_response
            values['inactive_response'] = inactive_response
            values['total_responses'] = total_responses
            values['assessed_response'] = assessed_response
            values['rubric_ids'] = slide.rubric_ids
            # if assessed_response:
            #     values['channel_progress'][slide.id]['quiz_karma_gain'] += assessed_response.xp_points
            #     values['channel_progress'][slide.id]['quiz_karma_won'] += assessed_response.xp_points
            for response in total_responses:
                if response.feedback == '<p><br></p>':
                    response.feedback = False
            values['peer_responses'] = request.env['open.response.rubric.staff'].search([
                ('user_id', '=', request.env.user.id),
                ('assess_type', '=', 'peer'),
                ('response_id.state', 'in', ['submitted', 'assessed']),
                ('response_id.slide_id', '=', slide.id)
            ]).mapped('response_id')
        return values

    @http.route('/slides/slide/get_values', website=True, type="json", auth="user")
    def slide_get_value(self, slide_id):
        csrf_token = request.csrf_token()
        slide = request.env['slide.slide'].browse(slide_id)
        if slide:
            values = {'slide': self._get_slide_values(slide), 'csrf_token': csrf_token}
            if slide.prompt_ids:
                values.update({
                    'slide_prompts': [{
                        'id': prompt.id,
                        'sequence': prompt.sequence,
                        'question': prompt.question_name,
                        'response_type': prompt.response_type,
                        'name': prompt.name,
                    } for prompt in slide.prompt_ids.sorted(key=lambda x: x.id)]
                })
            if slide.response_ids:
                total_responses = slide.response_ids.filtered(lambda l: l.user_id == request.env.user)
                values['total_responses'] = []
                for ora_response in total_responses:
                    if ora_response.feedback == '<p><br></p>':
                        ora_response.feedback = False
                    values['total_responses'].append(self._get_total_responses(ora_response, slide))
                peer_response_ids = request.env['open.response.rubric.staff'].search([
                    ('user_id', '=', request.env.user.id),
                    ('assess_type', '=', 'peer'),
                    ('response_id.state', 'in', ['submitted', 'assessed']),
                    ('response_id.slide_id', '=', slide.id)
                ])
                values['peer_responses'] = []
                for staff_response in peer_response_ids:
                    submitted_date = False
                    if staff_response.submitted_date:
                        submitted_date = staff_response.submitted_date.strftime('%d %B %Y')
                    values['peer_responses'].append(({
                        'id': staff_response.response_id.id,
                        'state': staff_response.state,
                        'assess_type': staff_response.assess_type,
                        'user_id': staff_response.user_id.id,
                        'submitted_date': submitted_date,
                        'option_ids': [{
                            'id': rubric_id.criteria_id.id,
                            'criterian_name': rubric_id.criteria_id.criterian_name,
                            'criteria_desc': rubric_id.criteria_desc,
                            'name': rubric_id.option_id.name,
                            'criteria_option_point': rubric_id.criteria_option_point,
                            'criteria_option_desc': rubric_id.criteria_option_desc,
                            'assess_explanation': rubric_id.assess_explanation,
                        } for rubric_id in staff_response.option_ids],
                        'user_response_line': [self._get_user_response(user_response_line) for user_response_line in staff_response.response_id.user_response_line]
                    }))
        return values

    def _get_slide_values(self, slide):
        return {
            'id': slide.id,
            'is_member': slide.channel_id.is_member,
            'is_preview': slide.is_preview,
            'peer_assessment': slide.peer_assessment,
            'user': request.env.user.id,
            'rubric_ids': [{
                'criterian_name': rubric.criterian_name,
                'name': rubric.name,
                'id': rubric.id,
                'criterian_ids': [{
                    'id': option.id,
                    'name': option.name,
                } for option in rubric.criterian_ids],
            }for rubric in slide.rubric_ids],
        }

    def _get_user_response(self, user_response_line):
        return {
            'prompt_id': user_response_line.prompt_id.id,
            'value_text_box': user_response_line.value_text_box,
            'value_richtext_box': user_response_line.value_richtext_box,
        }

    def _get_total_responses(self, ora_response, slide):
        submitted_date = False
        if ora_response.submitted_date:
            submitted_date = ora_response.submitted_date.strftime('%d %B %Y')
        return {
            'id': ora_response.id,
            'user': request.env.user.id,
            'state': ora_response.state,
            'feedback': ora_response.feedback,
            'staff_id': ora_response.sudo().staff_id.id,
            'staff_name': ora_response.sudo().staff_id.name,
            'user_name': ora_response.sudo().user_id.name,
            'submitted_date': submitted_date,
            'can_resubmit': ora_response.can_resubmit,
            'feedback_user_image_url': request.website.image_url(ora_response.sudo().staff_id, 'image_1920', size=256),
            'ora_res_user_image_url': request.website.image_url(ora_response.sudo().user_id, 'image_1920', size=256),
            'user_response_line': [self._get_user_response(user_response_line) for user_response_line in ora_response.user_response_line],
            'slide_rubric_staff_line': [{
                'state': staff_line.state,
                'assess_type': staff_line.assess_type,
                'user_id': staff_line.sudo().user_id.id,
                'option_ids': [{
                    'id': rubric_id.criteria_id.id,
                    'criterian_name': rubric_id.criteria_id.criterian_name,
                    'criteria_desc': rubric_id.criteria_desc,
                    'name': rubric_id.option_id.name,
                    'criteria_option_point': rubric_id.criteria_option_point,
                    'criteria_option_desc': rubric_id.criteria_option_desc,
                    'assess_explanation': rubric_id.assess_explanation,
                } for rubric_id in staff_line.option_ids],
            }for staff_line in ora_response.slide_rubric_staff_line],
            'rubric_ids': [{
                'criterian_name': rubric.criterian_name,
                'name': rubric.name,
                'id': rubric.id,
                'criterian_ids': [{
                    'id': option.id,
                    'name': option.name,
                } for option in rubric.criterian_ids],
            }for rubric in slide.rubric_ids],
    }

    @http.route('/submit/peer/response', type='http', auth="user", website=True)
    def submit_peer_response(self, **kwargs):
        slide = request.env['slide.slide'].sudo().browse(int(kwargs.get('slide_id')))
        if kwargs.get('response_id'):
            response_id = request.env['ora.response'].browse(int(kwargs.get('response_id')))
            for line in response_id.slide_rubric_staff_line:
                if line.user_id == request.env.user and line.assess_type == 'peer':
                    values = []
                    for criteria in response_id.slide_id.rubric_ids:
                        opt_key = ''
                        exp_key = ''
                        for option_id in criteria.criterian_ids:
                            opt_key = 'options_%s_%s' % (response_id.id, criteria.id)
                            exp_key = 'exp_%s_%s' % (response_id.id, criteria.id)
                            if opt_key in kwargs and exp_key in kwargs:
                                break
                        option_id = kwargs.get(opt_key)
                        values.append((0, 0, {
                            'criteria_id': criteria.id,
                            'option_id': int(option_id) if option_id else False,
                            'assess_explanation': kwargs.get(exp_key)
                        }))
                    line.option_ids = values
                    line.state = 'completed'
                    line.submitted_date = datetime.now()
        return request.redirect('/slides/slide/%s' % slug(slide))

    def _get_channel_progress(self, channel, include_quiz=False):
        result = super(WebsiteSlidesORA, self)._get_channel_progress(channel, include_quiz=include_quiz)
        slides = request.env['slide.slide'].sudo().search([('channel_id', '=', channel.id)])
        ora_response_ids = request.env['ora.response'].sudo().search([
            ('slide_id', 'in', slides.ids),
            ('state', '=', 'assessed'),
            ('user_id', '=', request.env.user.id)
        ])
        for ora_response in ora_response_ids:
            result[ora_response.slide_id.id]['quiz_karma_gain'] += ora_response.xp_points
            result[ora_response.slide_id.id]['quiz_karma_won'] += ora_response.xp_points
        return result
