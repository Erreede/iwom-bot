import requests, re, json, datetime, os, time
from bs4 import BeautifulSoup
from os.path import join

class iWom:
    def __init__(self, username, password, initial_date = datetime.datetime.now().strftime('%d/%m/%Y')):
        try:
            self.initial_date = datetime.datetime.strptime(initial_date,'%d/%m/%Y').date()
        except:
            print('The date format is incorrect, must be: dd/mm/yyyy')

        if (datetime.datetime.now().date() - self.initial_date).days >= 365:
            print('Can not record dates earlier than 365 days')  
            return None

        self.historical_date = datetime.datetime(2022, 1, 1).date()
        self.historical_date_num = 8036
        self.session = requests.Session()
        self.dxc_iwom_user = username
        self.dxc_iwom_password = password
        self.bank_holidays = get_leaves(os.getenv('github_repo'), 'bank_holidays.json')
        self.holidays = get_leaves(os.getenv('github_repo'), 'holidays.json')
        self.others = get_leaves(os.getenv('github_repo'), 'others.json')
        self.reduced_hours_days = get_leaves(os.getenv('github_repo'), 'reduced_hours_days.json')
        self.tags = dict()
        self.tld = 'https://www.bpocenter-dxc.com'
        self.third_step_url = '/iwom_web4/es-corp/app/home.aspx'
        self.final_url = '/iwom_web4/es-corp/app/Jornada/Reg_jornada.aspx'
        self.headers = { 
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.125 Safari/537.36',
        }
        self.form_headers = { 
            'Content-Type' : 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.125 Safari/537.36',
        }
        self.dates_list = dates_list(self)

        if len(self.dates_list) > 0:
            print('Starting the time register process')
            self.first_step()
        else:
            print('Nothing to do here')        

    def save_tags(self, text):
        self.tags = dict()
        soup = BeautifulSoup(text, features='html.parser')
        for tag in soup.find_all('input', type='hidden'):
            self.tags[tag.get('name')] = tag.get('value')         

    def replace_hex_escapes(self, text):
        pattern = re.compile(r'\\x([0-9A-Fa-f]{2})')
        def replace_match(match):
            return chr(int(match.group(1), 16))
        return pattern.sub(replace_match, text)            

    def first_step(self):
        r = self.session.get('https://portalwa1.bpocenter-dxc.com/External/Challenge?scheme=OpenIdConnect&returnUrl=%2F', allow_redirects=True)
        if r.status_code == 200:
            print('Accessing Okta')
            okta_data = BeautifulSoup(r.text, features='html.parser').find_all('script')[2]
            stateToken = self.replace_hex_escapes(re.search('stateToken\"\:\"(.*?)\"', format(okta_data))[1])
            if r.status_code == 200:
                print('Sending credentials to Okta')
                r = self.session.post('https://uid.dxc.com/api/v1/authn', json={
                    "password": self.dxc_iwom_password,
                    "username": self.dxc_iwom_user,
                    "options":{"warnBeforePasswordExpired": True,"multiOptionalFactorEnroll": True},
                    "stateToken": stateToken
                }, allow_redirects=True) 
                if r.status_code == 200:
                    print('Getting user config')
                    factor = r.json()['_embedded']['factors'][0]['id']
                    print(r.json())
                    r = self.session.post(f'https://uid.dxc.com/api/v1/authn/factors/{factor}/verify?autoPush=true&rememberDevice=true', json={"stateToken": stateToken}, allow_redirects=True)
                    while r.json()['status'] in ['MFA_REQUIRED', 'MFA_CHALLENGE']:
                        time.sleep(10)
                        r = self.session.post(f'https://uid.dxc.com/api/v1/authn/factors/{factor}/verify?autoPush=true&rememberDevice=true', json={"stateToken": stateToken}, allow_redirects=True)
                        
                    if r.status_code == 200:
                        r = self.session.get(f'https://uid.dxc.com/login/step-up/redirect?stateToken={stateToken}', allow_redirects=True)
                        self.save_tags(r.text)
                        r = self.session.post('https://portalwa1.bpocenter-dxc.com/signin-oidc-okta', data=self.tags)
                        r = self.session.get('https://portalwa1.bpocenter-dxc.com/', allow_redirects=True)
                        self.save_tags(r.text)
                        r = self.session.post('https://www.bpocenter-dxc.com/iwom_web4/es-corp/app/ValidarU_IS4.aspx', data=self.tags)
                        self.third_step()
                else:
                    print('Initial request failed in first step')       
        else:
            print('Initial request failed in first step')       

    def third_step(self):
        r = self.session.get(self.tld + self.third_step_url, headers=self.headers, allow_redirects=True)
        r = self.session.get(self.tld + self.final_url, headers=self.headers, allow_redirects=True)
        if r.status_code == 200:
            self.save_tags(r.text)
            date_obj = datetime.datetime.strptime(self.dates_list[0][1],'%d/%m/%Y').date()
            last_date = move_to_month(date_obj, self.fourth_step, datetime.datetime.now().replace(day=1).date())
            for date in self.dates_list:
                date_obj = datetime.datetime.strptime(date[1],'%d/%m/%Y').date()
                if date_obj.month != last_date.month:
                    last_date = move_to_month(date_obj, self.fourth_step, last_date)
                self.fifth_step(date)                    
        else:
            print('Failed accessing the Reg_jornada url in third step')   

    def fourth_step(self, date):
        data = {
            '__EVENTTARGET': 'ctl00$Sustituto$Calendar1',
            '__EVENTARGUMENT': get_month_first_day(date, self.historical_date, self.historical_date_num),            
        }
        r = self.session.post(self.tld + self.final_url, data={**self.tags, **data}, headers=self.form_headers, allow_redirects=True)
        if r.status_code == 200:
            self.save_tags(r.text)
        else:
            print('Error selecting the day in the fourth step')                    

    def fifth_step(self, date):
        data = {
            '__EVENTTARGET': 'ctl00$Sustituto$Calendar1',
            '__EVENTARGUMENT': date[2],
        }
        if date[0] == 'Regular': data['ctl00$Sustituto$Ch_disponible'] = 'on'
        r = self.session.post(self.tld + self.final_url, data={**self.tags, **data}, headers=self.form_headers, allow_redirects=True)
        if r.status_code == 200:
            self.save_tags(r.text)
            if date[0] == 'Regular':
                self.sixth_step(date)
            elif date[0] in ['Holiday', 'Other']:
                self.absent_check(date)
                self.save_absent(date)
        else:
            print('Error selecting the day in the fifth step')           

    def sixth_step(self, date):
        data = {
            '__EVENTTARGET': 'ctl00$Sustituto$Btn_Guardar',
            'ctl00$Sustituto$Ch_disponible': 'on',
            'ctl00$Sustituto$d_hora_inicio1': date[3],
            'ctl00$Sustituto$D_minuto_inicio1': 0,
            'ctl00$Sustituto$d_hora_final1': date[4],
            'ctl00$Sustituto$d_minuto_final1': 0,
            'ctl00$Sustituto$T_efectivo': date[5],
            'ctl00$Sustituto$Tx_diferencia': '00',
        }
        r = self.session.post(self.tld + self.final_url, data={**self.tags, **data}, headers=self.form_headers, allow_redirects=True)
        if r.status_code == 200:
            self.save_tags(r.text)
            print('Time recorded correctly ' + str(date))
        else:
            print('Error saving the hours in the sixth step')                         

    def absent_check(self, date):
        data = {
            '__EVENTTARGET': 'ctl00$Sustituto$D_absentismo',
            'ctl00$Sustituto$D_absentismo': date[3],
        }
        r = self.session.post(self.tld + self.final_url, data={**self.tags, **data}, headers=self.form_headers, allow_redirects=True)
        if r.status_code == 200:
            self.save_tags(r.text)
        else:
            print('Error checking the absent check')     

    def save_absent(self, date):
        data = {
            '__EVENTTARGET': 'ctl00$Sustituto$Btn_Guardar2',
            'ctl00$Sustituto$D_absentismo': date[3],
        }
        r = self.session.post(self.tld + self.final_url, data={**self.tags, **data}, headers=self.form_headers, allow_redirects=True)
        if r.status_code == 200:
            self.save_tags(r.text)
            print('Time recorded correctly ' + str(date))
        else:
            print('Error saving absent day')     

def dates_list(iwom):
    dates = []
    now = datetime.datetime.now().date()
    while iwom.initial_date <= now:        
        calculate_date_type(iwom, dates)
        iwom.initial_date = iwom.initial_date + datetime.timedelta(days=1)
    return dates

def calculate_date_type(iwom, dates):
    initial_date_str = iwom.initial_date.strftime('%d/%m/%Y')
    delta_days = str((iwom.initial_date - iwom.historical_date).days + iwom.historical_date_num)
    for other in iwom.others:
        if initial_date_str == other[0]:
            return dates.append(['Other', initial_date_str, delta_days, other[1]])
    if initial_date_str in iwom.bank_holidays:  
        return None
    if initial_date_str in iwom.holidays:  
        return dates.append(['Holiday', initial_date_str, delta_days, '14'] )
    else:
        if iwom.initial_date.month in [7, 8] and iwom.initial_date.weekday() <= 4:
            return dates.append(['Regular', initial_date_str, delta_days, '8', '15', '07:00'])         
        if iwom.initial_date.weekday() == 4 or initial_date_str in iwom.reduced_hours_days:
            return dates.append(['Regular', initial_date_str, delta_days, '9', '16', '07:00'])
        elif iwom.initial_date.weekday() < 4:
            return dates.append(['Regular', initial_date_str, delta_days, '9', '18', '08:28'])    

def calculate_month_delta(last_date, date):
    if last_date > date:
        return (last_date.year - date.year) * 12 + last_date.month - date.month   
    else:
        return (date.year - last_date.year) * 12 + date.month - last_date.month

def move_to_month(date, fourth_step, last_date):
    month_delta = calculate_month_delta(last_date, date)
    last_date = last_date.replace(day=1)
    while month_delta != 0:
        if last_date > date:
            last_date = (last_date - datetime.timedelta(days=1)).replace(day=1)     
        else:
            last_date = (last_date + datetime.timedelta(days=31)).replace(day=1)    
        fourth_step(last_date.strftime('%d/%m/%Y'))        
        month_delta -= 1            
    return last_date           
                
def get_month_first_day(date, initial_date, initial_date_num):  
    date = datetime.datetime.strptime(date,'%d/%m/%Y').date().replace(day=1)
    return 'V' + str((date - initial_date).days + initial_date_num)

def get_leaves(url, file):
    if url is not None:
        r = requests.get(url + '/' + file)
        if r.status_code == 200:
            return r.json()
    if os.path.exists(join('leaves', file)):
        return json.load(open(join('leaves', file)))
    print('File ' + file + ' not found, will not register')
    return []