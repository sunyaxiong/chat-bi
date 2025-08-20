import { NextApiRequest, NextApiResponse } from 'next';
import jwt from 'jsonwebtoken';

const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const sessionCookie = req.cookies.session;

  if (!sessionCookie) {
    return res.status(401).json({ authenticated: false });
  }

  try {
    const decoded = jwt.verify(sessionCookie, JWT_SECRET) as any;
    
    // 检查token是否过期
    if (decoded.exp && decoded.exp < Math.floor(Date.now() / 1000)) {
      return res.status(401).json({ authenticated: false });
    }

    return res.status(200).json({ authenticated: true });
  } catch (error) {
    return res.status(401).json({ authenticated: false });
  }
}