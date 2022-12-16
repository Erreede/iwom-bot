import requests, re, json, datetime
from bs4 import BeautifulSoup
from os.path import join

class iWom:
    def __init__(self, username, password, initial_date):
        try:
            self.initial_date = datetime.datetime.strptime(initial_date,'%d/%m/%Y').date()
            self.historical_date = datetime.datetime.strptime('01/01/2022','%d/%m/%Y').date()
            self.historical_date_num = 8036
        except:
            print('The date format is incorrect, must be: dd/mm/yyyy')
        self.session = requests.Session()
        self.tld = 'https://www.bpocenter-dxc.com/'
        self.dxc_iwom_user = username
        self.dxc_iwom_password = password
        self.tags = dict()
        self.first_step_url = 'iwom_web5/portal_apps.aspx'
        self.second_step_url = 'iwom_web5/Login.aspx'
        self.third_step_url = 'iwom_web4/es-corp/app/home.aspx'
        self.final_url = 'iwom_web4/es-corp/app/Jornada/Reg_jornada.aspx'
        self.headers = { 
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.125 Safari/537.36',
        }
        self.form_headers = { 
            'Content-Type' : 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.125 Safari/537.36',
        }
        self.dates_list = dates_list(self.initial_date, datetime.datetime.now().date(), self.historical_date, self.historical_date_num)

    def save_tags(self, text):
        self.tags = dict()
        soup = BeautifulSoup(text, features='html.parser')
        for tag in soup.find_all('input', type='hidden'):
            self.tags[tag.get('name')] = tag.get('value')         

    def first_step(self):
        r = self.session.get(self.tld + self.first_step_url, allow_redirects=True)
        if r.status_code == 200:
            self.save_tags(r.text)
            self.second_step()           
        else:
            print('Initial request failed in first step')

    def second_step(self):
        data = {
            'LoginApps$UserName': self.dxc_iwom_user,
            'LoginApps$Password': self.dxc_iwom_password,
            'LoginApps$btnlogin': 'Log in'
        }
        r = self.session.post(self.tld + self.second_step_url, data={**self.tags, **data}, headers=self.form_headers, allow_redirects=True)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, features='html.parser')
            r = soup.find(id='MainContent_tableitem1').attrs['onclick']
            rex = re.search('postwith\(\'(.*?)\'\,(.*?)\)', r)
            if rex.lastindex == 2:
                url = rex[1]
                auth = re.sub("(\w+):", r'"\1":',  rex[2]. replace("'", '"'))
                try:
                    print('Your internal iWom username is: ' + re.search('usuario\:\'(.*?)\'', rex[2])[1])
                except:
                    pass
                r = self.session.post(url, data=json.loads(auth), headers=self.form_headers, allow_redirects=True)
                if r.status_code == 200:
                    self.third_step()
                else:
                    print('Something went wrong in the user verification in second step')
            else:
                print('Regex to parse internal iWom credentials failed in second step')
        else:
            print('Initial post with credentials failed in second step')          

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
        }
        r = self.session.post(self.tld + self.final_url, data={**self.tags, **data}, headers=self.form_headers, allow_redirects=True)
        if r.status_code == 200:
            self.save_tags(r.text)
            print('Time recorded correctly ' + str(date))
        else:
            print('Error saving the hours in the fifth step')              

    def absent_check(self, date):
        data = {
            '__EVENTTARGET': 'ctl00$Sustituto$D_absentismo',
            'ctl00$Sustituto$D_absentismo': date[3],
        }
        r = self.session.post(self.tld + self.final_url, data={**self.tags, **data}, headers=self.form_headers, allow_redirects=True)
        if r.status_code == 200:
            self.save_tags(r.text)
        else:
            print('Error saving the hours in the fifth step')     

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
            print('Error saving the hours in the fifth step')     

def dates_list(initial_date, now, historical_date, historical_date_num):
    dates = []
    holidays = json.load(open(join('leaves', 'holidays.json')))
    bank_holidays = json.load(open(join('leaves', 'bank_holidays.json')))
    others = json.load(open(join('leaves', 'others.json')))
    while initial_date <= now:        
        check_date_type(others, holidays, bank_holidays, initial_date, historical_date, historical_date_num, dates)
        initial_date = initial_date + datetime.timedelta(days=1)
    return dates

def check_date_type(others, holidays, bank_holidays, initial_date, historical_date, historical_date_num, dates):
    initial_date_str = initial_date.strftime('%d/%m/%Y')
    delta_days = str((initial_date - historical_date).days + historical_date_num)
    for other in others:
        if initial_date_str == other[0]:
            return dates.append(['Other', initial_date_str, delta_days, other[1]])
    if initial_date_str in bank_holidays:  
        return None
    if initial_date_str in holidays:  
        return dates.append(['Holiday', initial_date_str, delta_days, '14'] )
    else:      
        if initial_date.weekday() == 4:
            return dates.append(['Regular', initial_date_str, delta_days, '9', '16', '7:00'])
        elif initial_date.weekday() < 5:
            return dates.append(['Regular', initial_date_str, delta_days, '9', '18', '8:28'])

def calculate_month_delta(date, initial_date):
    if date > initial_date:
        return (date.year - initial_date.year) * 12 + date.month - initial_date.month   
    else:
        return (initial_date.year - date.year) * 12 + initial_date.month - date.month

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