<h1>Extended Flask Base</h1>
<p>This is a template I made to simplify building basic websites. It is setup with contact form, basic email functionality through Gmail (up to 99 emails a day), integrates with a mailchimp signup page. It also includes an authentication blueprint and is prepared to build a simple database with a User model. Draws from <a href="https://github.com/miguelgrinberg/flasky" target="_blank">Miguel Grinberg's Flasky project</a> liberally.</p>
<h2>Getting Started</h2>
<p>To extend this base, clone it and navigate to the project home directory. Then create a virtual environment there with <code>python3 -m venv env</code>. Activate the environment by running <code>source env/bin/activate</code> and install the project dependencies with <code>pip install -r requirements.txt</code>. Next, create a new .env file in the root directory. In the .env file define the following variables:</p>
<ul>
  <li>SECRET_KEY=(your secret key)</li>
  <li>FLASK_APP=flask_base.py</li>
  <li>FLASK_CONFIG=(set this to development, testing, or production)</li>
  <li>MAIL_USERNAME=(your gmail account)</li>
  <li>MAIL_PASSWORD=(your gmail password)</li>
  <li>MAIL_SENDER=(string of name and email)</li>
  <li>MAIL_USE_TLS=True</li>
  <li>APP_ADMIN_MAIL=(contact form messages will be directed to this email)</li>
</ul>
<p>Note: If using Gmail, account settings must be updated to allow third party apps to send email</p>
<h2>Integrating Mailchimp</h2>
<p>The newsletter signup page is set up to redirect form posts to Mailchimp. To connect the page to your account, it's necessary to edit the following values in app/templates/newsletter_form.html:</p>
<ul>
  <li>form element: action</li>
  <li>hidden input (name: u) value</li>
  <li>hidden input (name: ui) value</li>
  <li>hidden input (name: ht) value</li>
 </ul>
 <p>Follow this useful guide for instructions specific to your mailchimp account: <a href="https://mailchimp.com/help/host-your-own-signup-forms/" target="_blank">mailchimp.com/help/host-your-own-signup-forms</a></p>
<h2>Database Setup</h2>
<p>This template uses Flask-Migrate to manage database migrations. To start, run:</p>
<p><code>$ flask db init</code></p>
<p><code>$ flask db migrate -m 'initial migration'</code></p>
<p><code>$ flask db upgrade</code></p>
<p>For further information see the <a href="https://flask-migrate.readthedocs.io/en/latest/" target="_blank">Flask-Migrate documentation</a></p>
