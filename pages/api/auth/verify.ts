import { NextApiRequest, NextApiResponse } from 'next';
import jwt from 'jsonwebtoken';

const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { token } = req.body;
  const expectedToken = process.env.ACCESS_TOKEN;

  if (token === expectedToken) {
    // 生成JWT会话token
    const sessionToken = jwt.sign(
      { 
        authenticated: true, 
        timestamp: Date.now(),
        exp: Math.floor(Date.now() / 1000) + (24 * 60 * 60) // 24小时过期
      },
      JWT_SECRET
    );

    // 设置HttpOnly cookie
    res.setHeader('Set-Cookie', [
      `session=${sessionToken}; HttpOnly; Path=/; Max-Age=${24 * 60 * 60}; SameSite=Strict`
    ]);

    return res.status(200).json({ success: true });
  } else {
    return res.status(401).json({ error: 'Invalid token' });
  }
}