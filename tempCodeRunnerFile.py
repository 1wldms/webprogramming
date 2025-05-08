   if user and user[0] == password:
                session['username'] = username
                flash('Welcome to Style-It 🎉')
                return redirect(url_for('index'))