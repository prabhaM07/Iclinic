import api from "../../../lib/axios";

export const initiateCall = (to_number: string): Promise<{ status: string; call_sid?: string }> =>
    api.post("/make-call", null, {
        params: { to_number }
    }).then(res => res.data);