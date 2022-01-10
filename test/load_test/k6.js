// K6 LOAD TEST

import http from 'k6/http';
import { check, sleep } from 'k6';

// Load test options
export const options = {
  stages: [
    { duration: '1m', target: 50 }, // Ramp-up of traffic from 1 to 50 users over 1 minute.
    { duration: '2m', target: 50 }, // Stay at 50 users for 2 minutes
    { duration: '1m', target: 0 }, // Ramp-down to 0 users
  ],
  // Thresholds to be checked
  thresholds: {
    'http_req_duration': ['p(95) < 2000'], // 95% of requests must complete below 2s
    'Login successful': ['p(95) < 500'], // 95% of requests must complete below 0.5s
    'QR creation successful': ['p(95) < 500'],
    'Get QR successful': ['p(95) < 500'],
    'Get QR image successful': ['p(95) < 500'],
    'QR update successful': ['p(95) < 500'],
    'QR deletion successful': ['p(95) < 500'],
    'Get QR stats successful': ['p(95) < 500'],
  },
};

// Shortcuts to be used in links
const URL = 'http://localhost:8000';
const NEWLINK = 'newlink';
const ID = '1';
const ID2 = '2';
const V = '1';
const SIZE = '512';

// Default function
export default () => {

  let cred = { username: 'user', password: 'pass', };
  let qr_link = { link: 'link', };
  let img = { qr_id: '2', version: '1', size: '512', };
  let id = { qr_id: '1', };
  let update = { qr_id: 2, new_link: 'newlink', };
  
  const params = {
    headers: {
    'accept': 'application/json',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Authorization': 'Bearer 2',
    },
  };
  
  const multi = {
    headers: {
    'accept': 'application/json',
    // 'Content-Type': 'application/x-www-form-urlencoded',
    'Authorization': 'Bearer 2',
    },
  };
  
  // Login post function - POST

  const login = http.post(`${URL}/login`, cred,);

  check(login, {
  'Login successful': (res1) => res1.json('access') !== '',
  '↑ Login Response 200 ↑': (r1) => r1.status === 200,
  });
  
  // Create qr function - POST
  
  const create_qr = http.post(`${URL}/create_qr`, qr_link, params);
  
  check(create_qr, {
  'QR creation successful': (res2) => res2.json('link') !== '',
  '↑ Create Response 200 ↑': (r2) => r2.status === 200,
  });
  
  // Get qr function - GET
  
  const get_qr = http.get(`${URL}/my_qr_codes`, params);
  
  check(get_qr, {
  'Get QR successful': (res3) => res3.json('id', 'link') !== '',
  '↑ Get QR Response 200 ↑': (r3) => r3.status === 200,
  });
  
  // Get image function - POST
  
  const get_image = http.post(`${URL}/get_qr_img?qr_id=${ID2}`, {}, multi);
  
  check(get_image, {
  'Get QR image successful': (res4) => res4.json('image') !== '',
  '↑ Get Image Response 200 ↑': (r4) => r4.status === 200,
  });
  
  // Update qr function - POST
  
  const update_qr = http.post(`${URL}/update_qr?qr_id=${ID2}&new_link=${NEWLINK}`, update, params);
  
  check(update_qr, {
  'QR update successful': (res5) => res5.json('newlink') !== '',
  '↑ Update Response 200 ↑': (r5) => r5.status === 200,
  });
  
  // Delete qr function - POST
  
  const delete_qr = http.post(`${URL}/delete_qr?qr_id=${ID}`, id, params);
  
  check(delete_qr, {
  'QR deletion successful': (res6) => res6.json('deleted') !== '',
  '↑ Delete Response 200 ↑': (r6) => r6.status === 200,
  });
  
  // Get stats function - GET
  
  const get_stats = http.get(`${URL}/get_qr_stats?qr_id=${ID}`, params);
  
  check(get_stats, {
  'Get QR stats successful': (res7) => res7.json('stats') !== '',
  '↑ Stats Response 200 ↑': (r7) => r7.status === 200,
  });
  
  sleep(1);
};

