
    @app.get("/v1/creator/<id>")
    @token_required
    def get_creator(current_user, id):
        """
        get a creator
        ---
        tags: ['mod']
        parameters:
              - in: path
                name: id
                schema:
                    type: integer
        responses:
            200:
                schema:
                    type: object
                    properties:
                        username:
                            type: string
            404:
                schema:
                    type: object
        """

        try:
            creator = Creator.query.filter_by(id=id).first_or_404()
        except Exception as e:
            app.logger.warning(msg=repr(e))
            return jsonify({"message": "Couldn't find creator."}), 401

        return jsonify(creator.name, creator.id), 200

    @app.post("/v1/add_creator")
    @token_required
    def add_creator(current_user):
        """
        add a creator
        ---
        tags: ['mod']
        requestBody:
            content:
                application/json:
                    schema:
                        type: object
                        properties:
                            name:
                                type: string
        responses:
            200:
                schema:
                    type: object
                    properties:
                        username:
                            type: string
            401:
                schema:
                    type: object
        """

        try:
            name = request.json.get("name")

            new_creator = Creator(name=name)

            db.session.add(new_creator)
            db.session.commit()
        except Exception as e:
            app.logger.warning(msg=repr(e))
            return jsonify({"message": "Couldn't add creator."}), 401

        return jsonify({"name": name, "id": new_creator.id}), 200

    @app.get("/v1/level/<id>")
    @token_optional
    def get_level(current_user, id):
        """
        get a level
        ---
        tags: ['mod']
        parameters:
              - in: path
                name: id
                schema:
                    type: integer
        responses:
            200:
                schema:
                    type: object
                    properties:
                        level:
                            type: string
            404:
                schema:
                    type: object
        """

        try:
            level = Level.query.filter_by(id=id).first_or_404()
        except Exception as e:
            app.logger.warning(msg=repr(e))
            return jsonify({"message": "Couldn't find level."}), 401

        return jsonify(level), 200

    @app.post("/v1/add_level")
    @token_required
    def add_level(current_user):
        """
        add a level
        ---
        tags: ['mod']
        requestBody:
            content:
                application/json:
                    schema:
                        type: object
                        properties:
                            name:
                                type: string
                            host_id:
                                type: integer
        responses:
            200:
                schema:
                    type: object
                    properties:
                        username:
                            type: string
            401:
                schema:
                    type: object
        """

        try:
            name: str = request.json.get("name")
            host_id: int = request.json.get("host_id")

            new_level = Level(name=name, author_host=host_id)

            db.session.add(new_level)
            db.session.commit()

        except Exception as e:
            app.logger.warning(msg=repr(e))
            return jsonify({"message": "Couldn't add level."}), 40

        # return jsonify({new_level.id, new_level.author_host, new_level.name}), 200
        return (
            jsonify(
                {
                    "id": new_level.id,
                    "host_id": new_level.author_host,
                    "name": new_level.name,
                }
            ),
            200,
        )


    # @app.route('/auth/oauth2/google/')
    # def google():
    #
    #     # Google Oauth Config
    #     # Get client_id and client_secret from environment variables
    #     # For developement purpose you can directly put it
    #     # here inside double quotes
    #     GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    #     GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    #     GOOGLE_DISCOVERY_URL = (
    #         "https://accounts.google.com/.well-known/openid-configuration"
    #     )
    #
    #     CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
    #     oauth.register(
    #         name='google',
    #         client_id=GOOGLE_CLIENT_ID,
    #         client_secret=GOOGLE_CLIENT_SECRET,
    #         server_metadata_url=CONF_URL,
    #         client_kwargs={
    #             'scope': 'openid email profile'
    #         }
    #     )
    #
    #     # Redirect to google_auth function
    #     redirect_uri = url_for('google_auth', _external=True)
    #     return oauth.google.authorize_redirect(redirect_uri)
    #
    # @app.route('/google/auth/')
    # def google_auth():
    #     token = oauth.google.authorize_access_token()
    #     user = oauth.google.parse_id_token(token)
    #     print(" Google User ", user)
    #     return redirect('/')
