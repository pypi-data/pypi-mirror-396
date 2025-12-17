# Determine which tax period to be calculated
def tax_period_func() :
    a = 'k' 
    while a not in ['1','2','3']:
        print('Enter 1 for weekly tax_period')
        print('Enter 2 for monthly tax_period')
        print('Enter 3 for yearly tax_period')
        a= input('Choose a tax period: ')
        if a == '1':
            return a
        if a == '2':
            return a
        if a == '3':
            return a
    

# Accept input to determine how much is paid towards pension 
def pension_func():
    value = 'a'
    while True :
        print('How many percent of your salary is paid to pension?')
        
        try:
            value= int(input('Enter pension percentage or 0 if you optioned out of pension'))
            if int(value) >= 0 <= 100:
                break
            else:
                print('\n Enter a Valid Number between 0-100')
                value=  'a'
        except:
            print('\n Enter numeric value')
            pass
    return int(value)




# Determine if pension is deducted from overtime
def overtime_pension_func() :
    a = 0
    while a not in ['1','2']:
        print('Does your company Deduct pension from Overtime')
        a = input('Enter "1" for Yes or Not Sure, "2" for No.')
        if a == '1':
            return a
        if a == '2':
            return a


# Accept input for basic salary earning for the specific period
def wages_function():
    while True:
        value = input('Enter basic income excluding overtime for the specific period: ')
        try:
            value = float(value)
            if value >= 0:
                return value
            else:
                print('Please enter a non-negative number.')
        except ValueError:
            print('Enter a valid amount (e.g., 1500.00).')



# Accept input for how much is paid as overtime for the specific period
def overtime_amount():
    while True:
        value = input('Enter overtime income for the specific period- ')
        try:
            value = float(value)
            if value >= 0:
                return value
            else:
                print('Please enter a non-negative number.')
        except ValueError:
            print('Enter a valid amount (e.g., 1500.00).')


# Helps determine tax code to assign tax-free allowance
def tax_code_function():
    v = '0'
    while v not in ['1','2','3','4','5','6','7','8']:
        print('For tax_code 1257L, Enter 1')
        print('For tax_code 1257M, Enter 2')
        print('For tax_code 1257N, Enter 3')
        print('For tax_code BR, Enter 4')
        print('For tax_code DO, Enter 5')
        print('For tax_code D1, Enter 6 ')
        print('For tax_code X, Enter 7')
        print('If you do not know your tax_code, Enter  8')
        
        v = input('Choose a tax code')
        if v == '1' or v == '8':
            return 12570
        elif v == '2':
            return 13830
        elif v =='3':
            return 11310
        elif v == '4' or v == '7':
            print('Taxed at 20%')
            return 'BR'
        elif v == '5':
            print('Taxed at 40% with no Personal Allowance')
            return 'D0'
        elif v == '6':
            print('Taxed at 45% with no Personal Allowance ')
            return 'D1'             
    return v




# Calculated how much is paid to pension, tax, national insurance and take home for specific period.
def calculator(tax_period, personal_allowance, pension_percentage, basic_income, overtime_income, overtime_pension):
    
    pension = 0
    income = 0
    national_insurance = 0
    income_tax = 0

    # Calculate for weekly
    if tax_period == '1':
        
         # Calculate how much is paid to pension
        if overtime_pension == '1': 
            income = basic_income + overtime_income
            pension = income * pension_percentage / 100
            
        else:
            pension = basic_income * pension_percentage / 100
            income = basic_income + overtime_income
        
        # Calculate how much National Insurance is paid
        total_income = income - pension
        if 242 < total_income <= 967:
            national_insurance = 0.08 * (total_income - 242)
         
        elif total_income > 967:
            national_insurance = (0.08 * (967 - 242)) + (0.02 * (total_income - 967))
        
            
        # Calculate how much is paid to income tax based on tax-coode
        if personal_allowance == 'BR':
            income_tax = total_income * 0.2 
            
        elif personal_allowance == 'D0':
                income_tax = total_income * 0.4
            
        elif personal_allowance == 'D1':
            income_tax = total_income * 0.45
            
        else:
            
            #Personal allowance is divided by 52 because it is a weekly calculation
            personal_allowance = personal_allowance / 52 
            
            if total_income > personal_allowance:
                if total_income <= 967 :
                    income_tax = (total_income - personal_allowance) * 0.2
                    
                elif total_income <= 1923:
                    income_tax = ((967 - personal_allowance) * 0.2 + (total_income - 967) * 0.4)
                    
                elif total_income <= 2406:
                    excess = total_income - 1923
                    new_allowance = max(0, personal_allowance - (excess * 0.5))
                    income_tax = ((967 - new_allowance) * 0.2 + (total_income - 967) * 0.4)
                    
                else:
                    income_tax =(967 * 0.2 +(2406 - 967) * 0.4 + (total_income - 2406) * 0.45)
                    
    # Calcultate for Monthly
    elif tax_period == '2':
        
        # Calculate how much is paid to pension
        if overtime_pension == '1': 
            income = basic_income + overtime_income
            pension = income * pension_percentage / 100
            
        else:
            pension = basic_income * pension_percentage / 100
            income = basic_income + overtime_income
            
        # Calculate how much National Insurance is paid
        total_income = income - pension
        if total_income > 1048 and total_income <= 4189:
            national_insurance = 0.08 * (total_income - 1048)
         
        elif total_income > 4189:
            national_insurance = (0.08 * (4189 - 1048)) + (0.02 * (total_income - 4189))
            
        # Calculate how much is paid to income tax based on tax-coode
        if personal_allowance == 'BR':
            income_tax = total_income * 0.2 
                
        elif personal_allowance == 'D0':
            income_tax = total_income * 0.4
            
        elif personal_allowance == 'D1':
            income_tax = total_income * 0.45
            
        else:
            
            # Personal allowance is divided by 12 because it is a monthly calculation
            personal_allowance = personal_allowance / 12 
            if total_income > personal_allowance:
                if total_income <= 4189 :
                    income_tax = (total_income - personal_allowance) * 0.2
                    
                elif total_income <= 8333.33:
                    income_tax = ((4189 - personal_allowance) * 0.2 + (total_income - 4189) * 0.4)
                    
                elif total_income <= 10428.33:
                    excess = total_income - 8333.33
                    new_allowance = max(0, personal_allowance - (excess * 0.5))
                    income_tax = ((4189 - new_allowance) * 0.2 + (total_income - 4189) * 0.4)
                    
                else:
                    income_tax =(4189 * 0.2 +(10428.33 - 4189) * 0.4 + (total_income - 10428.33) * 0.45)
                    
    # Calculate for yearly    
    elif tax_period == '3':
        
        # Calculate how much is paid to pension
        if overtime_pension == '1': 
            income = basic_income + overtime_income
            pension = income * pension_percentage / 100
            
        else:
            pension = basic_income * pension_percentage / 100
            income = basic_income + overtime_income
            
        # Calculate how much National Insurance is paid
        total_income = income - pension
        if total_income > 12570 and total_income <= 50270:
            national_insurance = 0.08 * (total_income - 12570)
         
        elif total_income > 50270:
            national_insurance = (0.08 * (50270 - 12570)) + (0.02 * (total_income - 50270))
            
        # Calculate how much is paid to income tax based on tax-coode
        if personal_allowance == 'BR':
            income_tax = total_income * 0.2 
            
            
        elif personal_allowance == 'D0':
            
            income_tax = total_income * 0.4
        elif personal_allowance == 'D1':
            income_tax = total_income * 0.45
            
        else:
            
            #Personal allowance remains the same because it is based on yearly calculation
            if total_income > personal_allowance:
                if total_income <= 50270:
                    income_tax = (total_income - personal_allowance) * 0.2
                    
                elif total_income <= 100000:
                    income_tax = ((50270 - personal_allowance) * 0.2 + (total_income - 50270) * 0.4)
                    
                elif total_income <= 125140:
                    excess = total_income - 100000
                    new_allowance = max(0, personal_allowance - (excess * 0.5))
                    income_tax = ((50270 - new_allowance) * 0.2 + (total_income - 50270) * 0.4)
                    
                else:
                    income_tax =(50270 * 0.2 +(125140 - 50270) * 0.4 + (total_income - 125140) * 0.45)
                    
    print(f'Pension for this period is - {round(pension,2)}') 
    print(f'National Insurance paid for this period is - {round(national_insurance,2)}')
    take_home = round(income - pension - income_tax - national_insurance,2)
    print(f'Your Take Home Income is {take_home}')   


def income_calculator():
    tax_period = tax_period_func()
    pension_percentage = pension_func()
    personal_allowance = tax_code_function()
    overtime_pension = overtime_pension_func()
    basic_income = wages_function()
    overtime_income = overtime_amount()
    calculator(tax_period, personal_allowance,pension_percentage,basic_income,overtime_income, overtime_pension)

