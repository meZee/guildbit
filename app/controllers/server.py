import json

from flask import render_template, request, redirect, url_for, jsonify, Response
from flask.ext.classy import FlaskView, route

from app import db
from app.models import Server, Rating
import app.murmur as murmur
from app.util import support_jsonp


## Server views
class ServerView(FlaskView):
    def index(self):
        return redirect(url_for('home'))

    def get(self, id):
        ip = request.remote_addr
        server = Server.query.filter_by(uuid=id).first_or_404()
        rating = Rating.query.filter_by(server_uuid=id, ip=ip).first()

        server_details = murmur.get_server(server.mumble_host, server.mumble_instance)
        if server_details is not None:
            return render_template('server.html', server=server, details=server_details, rating=rating)
        else:
            return render_template('server_expired.html', server=server, rating=rating)

    @route('/<id>/expired')
    def expired(self, id):
        ip = request.remote_addr
        server = Server.query.filter_by(uuid=id).first_or_404()
        rating = Rating.query.filter_by(server_uuid=id, ip=ip).first()
        return render_template('server_expired.html', server=server, rating=rating)

    @route('/<id>/users/')
    def users(self, id):
        server = Server.query.filter_by(uuid=id).first_or_404()
        server_details = murmur.get_server(server.mumble_host, server.mumble_instance)
        if server_details is not None:
            users = {
                'count': server_details['user_count'],
                'users': server_details['users'],
                'sub_channels': server_details['sub_channels']
            }
            return jsonify(users=users)
        else:
            return jsonify(users=None)

    @route('/<id>/rating', methods=['POST'])
    @route('/<id>/expired/rating', methods=['POST'])
    def rating(self, id):
        ip = request.remote_addr
        stars = request.form['stars']

        r = Rating.query.filter_by(server_uuid=id, ip=ip).first()

        if r is None:
            try:
                r = Rating()
                r.server_uuid = id
                r.ip = ip
                r.stars = stars
                db.session.add(r)
                db.session.commit()
            except:
                import traceback

                db.session.rollback()
                traceback.print_exc()

            return jsonify(message='success')
        else:
            r.stars = stars
            db.session.commit()

        return jsonify(message=r.stars)

    @route('/<id>/feedback', methods=['POST'])
    @route('/<id>/expired/feedback', methods=['POST'])
    def feedback(self, id):
        ip = request.remote_addr
        feedback = request.form['feedback']

        if feedback:
            try:
                r = Rating.query.filter_by(server_uuid=id, ip=ip).first()
                r.feedback = feedback
                db.session.commit()
            except:
                import traceback

                db.session.rollback()
                traceback.print_exc()

            return jsonify(message='success')

        return jsonify(message='error')

    @support_jsonp
    @route('/<id>/cvp/')
    def cvp(self, id):
        server = Server.query.filter_by(uuid=id).first_or_404()
        server_details = murmur.get_server(server.mumble_host, server.mumble_instance)

        root_channel = server_details['parent_channel']
        sub_channels = server_details['sub_channels']
        root_channel['channels'] = sub_channels

        # channels = [dict(root_channel)] + sub_channels

        if server_details is not None:
            cvp = {
                'root': root_channel,
                'id': server_details['id'],
                'name': server_details['name'],
                "x_connecturl": "mumble://",
                'x_uptime': server_details['uptime']
            }
            # return jsonify(users=users)
            return Response(json.dumps(cvp, sort_keys=True, indent=4), mimetype='application/json')

        else:
            return jsonify(users=None)
