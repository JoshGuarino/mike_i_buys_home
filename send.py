import yaml
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import csv
import progressbar


# Function for sending email using sendgrid.
def send_email(name, address, email, sendgrid_client, config):

    # Load email body from cnfig and format with proper vars.
    email_body = config['email_body'].format(name=name, address=address)

    #Configure the message.
    message = Mail(
        from_email=config['from_email'],
        to_emails=email,
        subject=config['subject'],
        html_content=email_body)

    # Send it out.
    try:
        response = sendgrid_client.send(message)
        if response.status_code >= 200 and response.status_code < 300:
            return
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)



# Main function entry point.
def main():
    #load config for apikey and iniate apiclient.
    with open('config.yaml') as f:
        config = yaml.safe_load(f)
    sendgrid_client = SendGridAPIClient(config['sg_api_key'])

    #extracting data from csv file
    records = []
    with open(config['file_name']) as f:
        csv_first_row = f.readline()
        csv_col_names = csv_first_row.split(',')

        for i in range(len(csv_col_names)):
            if csv_col_names[i] == 'property_address_full':
                prop_add_index = i
            elif csv_col_names[i] == 'owner_name':
                owner_name_index = i
            elif csv_col_names[i] == 'email_addresses':
                email_add_index = i

        csv_file = csv.reader(f)
        for row in csv_file:
            if row[email_add_index] == '':
                continue
            email_address = row[email_add_index].split(',') 
            name = row[owner_name_index]
            prop_address = row[prop_add_index]
            records.append( {'name':name, 'address':prop_address, 'emails':email_address} )
    
    #send out emails using sendgrid api iterating through records.
    email_count = 0
    for record in progressbar.progressbar(records, prefix='Sending emails...'):
        for email in record['emails']:
            send_email(record['name'], record['address'], email, sendgrid_client, config)
            email_count += 1
    print(f'{email_count} emails sent out.')



if __name__ == "__main__":
    main()