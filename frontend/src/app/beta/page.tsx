'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card } from '@/components/ui/Card';

export default function BetaSignup() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    business: '',
    phone: '',
    message: ''
  });
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    // Simulate form submission (replace with actual Airtable/Google Forms integration)
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    setIsSubmitted(true);
    setIsLoading(false);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  if (isSubmitted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-pink-50 via-cream-50 to-gold-50 flex items-center justify-center p-4">
        <Card className="max-w-md w-full text-center p-8">
          <div className="mb-6">
            <div className="w-16 h-16 bg-gold-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-gold-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="text-2xl font-serif font-bold text-slate-800 mb-2">Thank You!</h2>
            <p className="text-slate-600">
              We've received your beta signup request. You'll be among the first to know when Melbourne Celebrant Portal launches.
            </p>
          </div>
          <Button 
            onClick={() => window.location.href = '/'}
            variant="primary"
            className="w-full"
          >
            Back to Home
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-cream-50 to-gold-50">
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-serif font-bold text-slate-800 mb-4">
              Join the Beta
            </h1>
            <p className="text-xl text-slate-600 max-w-2xl mx-auto">
              Be among the first Australian celebrants to experience the future of practice management. 
              Get early access to Melbourne Celebrant Portal.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-12 items-start">
            {/* Beta Benefits */}
            <div>
              <h2 className="text-2xl font-serif font-bold text-slate-800 mb-6">Beta Benefits</h2>
              <div className="space-y-4">
                {[
                  { icon: '🎯', title: 'Early Access', desc: 'Be first to use all premium features' },
                  { icon: '💰', title: 'Free for 6 Months', desc: 'Full access at no cost during beta' },
                  { icon: '🛠️', title: 'Shape the Product', desc: 'Your feedback directly influences development' },
                  { icon: '📞', title: 'Direct Support', desc: 'Personal onboarding and priority support' },
                  { icon: '🔒', title: 'Lifetime Discount', desc: '50% off when you upgrade to paid plan' },
                  { icon: '🏆', title: 'Founder Status', desc: 'Recognition as a founding user' }
                ].map((benefit, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <span className="text-2xl">{benefit.icon}</span>
                    <div>
                      <h3 className="font-semibold text-slate-800">{benefit.title}</h3>
                      <p className="text-slate-600 text-sm">{benefit.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Signup Form */}
            <Card className="p-8">
              <h2 className="text-2xl font-serif font-bold text-slate-800 mb-6">Reserve Your Spot</h2>
              <form onSubmit={handleSubmit} className="space-y-4">
                <Input
                  label="Full Name"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                  placeholder="Your full name"
                />
                
                <Input
                  label="Email Address"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  placeholder="your@email.com"
                />
                
                <Input
                  label="Business Name"
                  name="business"
                  value={formData.business}
                  onChange={handleChange}
                  placeholder="Your celebrant business name"
                />
                
                <Input
                  label="Phone Number"
                  name="phone"
                  type="tel"
                  value={formData.phone}
                  onChange={handleChange}
                  placeholder="Your phone number"
                />
                
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    What's your biggest challenge? (Optional)
                  </label>
                  <textarea
                    name="message"
                    value={formData.message}
                    onChange={handleChange}
                    rows={3}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-gold-500 focus:border-transparent"
                    placeholder="Tell us about your current workflow challenges..."
                  />
                </div>
                
                <Button
                  type="submit"
                  variant="primary"
                  size="lg"
                  className="w-full"
                  loading={isLoading}
                >
                  {isLoading ? 'Submitting...' : 'Join Beta Waitlist'}
                </Button>
                
                <p className="text-xs text-slate-500 text-center">
                  By signing up, you agree to receive updates about Melbourne Celebrant Portal. 
                  We respect your privacy and won't spam you.
                </p>
              </form>
            </Card>
          </div>

          {/* Social Proof */}
          <div className="mt-16 text-center">
            <p className="text-slate-600 mb-8">Trusted by celebrants across Australia</p>
            <div className="flex justify-center items-center space-x-8 opacity-60">
              <div className="text-2xl">🇦🇺</div>
              <div className="text-sm font-medium">Melbourne</div>
              <div className="text-sm font-medium">Sydney</div>
              <div className="text-sm font-medium">Brisbane</div>
              <div className="text-sm font-medium">Perth</div>
              <div className="text-sm font-medium">Adelaide</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 