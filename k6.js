import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '10m', target: 1000 }, // Ramp-up of traffic from 1 to 1000 users over 10 minutes.
    { duration: '20m', target: 1000 }, // Stay at 1000 users for 20 minutes
    { duration: '10m', target: 0 }, // Ramp-down to 0 users
  ],
  thresholds: {
    'http_req_duration': ['p(95) < 500'], // 95% of requests must complete below 500ms
    'login successful': ['p(95) < 500'],
    'qr creation successful': ['p(95) < 500'],
    'get qr successful': ['p(95) < 500'],
    'get qr image successful': ['p(95) < 500'],
    'qr update successful': ['p(95) < 500'],
    'qr deletion successful': ['p(95) < 500'],
    'get qr stats successful': ['p(95) < 500'],
  },
};

const BASE_URL = 'http://localhost:8000/docs#/default';
const USERNAME = 'user';
const PASSWORD = 'pass';
const LINK = 'link';
const NEWLINK = 'newlink';
const ID = '1';
const VERSION = '1';
const SIZE = '1024';

export default () => {

  const login = http.post(`${BASE_URL}/login_login_post/`, { username: USERNAME, password: PASSWORD, });

  check(login, { 'login successful': (res1) => res1.json('access') !== '', });
  
  const create_qr = http.post(`${BASE_URL}/create_qr_create_qr_post`, { link: LINK, });
  
  check(create_qr, {'qr creation successful': (res2) => res2.json('link') !== '',});
  
  const get_qr = http.get(`${BASE_URL}/my_qr_codes_my_qr_codes_get`);
  
  check(get_qr, {'get qr successful': (res3) => res3.json('id', 'link') !== '',});
  
  const get_image = http.post(`${BASE_URL}/get_qr_img_get_qr_img_post`,
  { qr_id: ID, version: VERSION, size: SIZE, });
  
  check(get_qr, {'get qr image successful': (res4) => res4.json('image') !== '',});
  
  const update_qr = http.post(`${BASE_URL}/update_qr_update_qr_post`, { link: NEWLINK, });
  
  check(update_qr, {'qr update successful': (res5) => res5.json('newlink') !== '',});
  
  const delete_qr = http.post(`${BASE_URL}/delete_qr_delete_qr_post`, { qr_id: ID, });
  
  check(delete_qr, {'qr deletion successful': (res6) => res6.json('deleted') !== '',});
  
  const get_stats = http.get(`${BASE_URL}/get_qr_stats_get_qr_stats_get`, { qr_id: ID, });
  
  check(get_stats, {'get qr stats successful': (res7) => res7.json('stats') !== '',});
  
  sleep(1);
};

