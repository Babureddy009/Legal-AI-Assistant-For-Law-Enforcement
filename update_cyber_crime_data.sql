-- Update IPC sections for cyber crimes
UPDATE ipc_sections 
SET description = 'Sending offensive messages through communication service',
    punishment = 'Imprisonment up to 3 years and fine'
WHERE section_number = '66A';

UPDATE ipc_sections 
SET description = 'Dishonestly receiving stolen computer resource or communication device',
    punishment = 'Imprisonment up to 3 years or fine up to Rs. 1 lakh or both'
WHERE section_number = '66B';

UPDATE ipc_sections 
SET description = 'Identity theft and cheating by personation using computer resource',
    punishment = 'Imprisonment up to 3 years and fine up to Rs. 1 lakh'
WHERE section_number = '66C';

UPDATE ipc_sections 
SET description = 'Cheating by personation using computer resource',
    punishment = 'Imprisonment up to 3 years and fine up to Rs. 1 lakh'
WHERE section_number = '66D';

UPDATE ipc_sections 
SET description = 'Violation of privacy',
    punishment = 'Imprisonment up to 3 years or fine up to Rs. 2 lakhs or both'
WHERE section_number = '66E';

UPDATE ipc_sections 
SET description = 'Cyber terrorism',
    punishment = 'Imprisonment for life'
WHERE section_number = '66F'; 