import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    vus: 10,
    duration: '15s',
    thresholds: {
        http_req_duration: ['p(95)<500'],
        http_req_failed: ['rate<0.01'],
    },
};

const BASE_URL = __ENV.API_URL || 'http://backend:8000';

export default function () {
    const res = http.get(`${BASE_URL}/api/appointments`);
    check(res, {
        'status is 200': (r) => r.status === 200,
    });
    sleep(0.5);
}
