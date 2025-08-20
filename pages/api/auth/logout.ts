import { NextApiRequest, NextApiResponse } from 'next';

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  // 清除session cookie
  res.setHeader('Set-Cookie', [
    'session=; HttpOnly; Path=/; Max-Age=0; SameSite=Strict'
  ]);

  return res.status(200).json({ success: true });
}