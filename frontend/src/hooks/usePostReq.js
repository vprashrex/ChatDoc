import axios from "axios";
import { useState } from "react";
import { toast } from 'react-toastify';

export function usePostReq(url) {
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);


  async function execute(payload = {}) {
    setLoading(true);
    return await toast.promise(axios
      .post(
        "http://localhost:8000/" + url,
        payload,{withCredentials: true}
      ),{pending:"Request is Processing"},{className:"toast-processing-message",position:"top-center"})
    .then((res) => res.data)
    .finally(() => setLoading(false));
  }
  return { execute, error, loading, setError, setLoading };
}