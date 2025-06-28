'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card } from '@/components/ui/Card';
import { Heart, ArrowLeft } from 'lucide-react';

export default function BetaSignupPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    business_name: '',
    abn: '',
    experience_years: '',
    ceremonies_per_year: '',
    current_software: '',
    pain_points: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      // Beta signup functionality will be implemented here
      console.log('Beta signup form submitted:', formData);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Show success message and redirect
      alert('Thanks for your interest! We\'ll be in touch soon.');
      router.push('/');
    } catch (error) {
      console.error('Beta signup error:', error);
      alert('Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-secondary via-background to-accent-light py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center text-primary hover:text-primary-dark mb-8">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Home
          </Link>
          <div className="flex justify-center mb-4">
            <div className="bg-primary/10 p-3 rounded-full">
              <Heart className="h-8 w-8 text-primary" />
            </div>
          </div>
          <h1 className="text-4xl font-serif font-bold text-primary-dark mb-4">
            Join Our Beta Program
          </h1>
          <p className="text-lg text-foreground/70">
            Be among the first to experience the future of celebrant business management
          </p>
        </div>

        <Card className="p-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-4">
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                  Full Name
                </label>
                <Input
                  id="name"
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="mt-1"
                />
              </div>

              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                  Email Address
                </label>
                <Input
                  id="email"
                  type="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="mt-1"
                />
              </div>

              <div>
                <label htmlFor="phone" className="block text-sm font-medium text-gray-700">
                  Phone Number
                </label>
                <Input
                  id="phone"
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  className="mt-1"
                />
              </div>

              <div>
                <label htmlFor="business_name" className="block text-sm font-medium text-gray-700">
                  Business Name
                </label>
                <Input
                  id="business_name"
                  type="text"
                  required
                  value={formData.business_name}
                  onChange={(e) => setFormData({ ...formData, business_name: e.target.value })}
                  className="mt-1"
                />
              </div>

              <div>
                <label htmlFor="abn" className="block text-sm font-medium text-gray-700">
                  ABN
                </label>
                <Input
                  id="abn"
                  type="text"
                  value={formData.abn}
                  onChange={(e) => setFormData({ ...formData, abn: e.target.value })}
                  className="mt-1"
                />
              </div>

              <div>
                <label htmlFor="experience_years" className="block text-sm font-medium text-gray-700">
                  Years of Experience as a Celebrant
                </label>
                <Input
                  id="experience_years"
                  type="number"
                  min="0"
                  value={formData.experience_years}
                  onChange={(e) => setFormData({ ...formData, experience_years: e.target.value })}
                  className="mt-1"
                />
              </div>

              <div>
                <label htmlFor="ceremonies_per_year" className="block text-sm font-medium text-gray-700">
                  Average Number of Ceremonies per Year
                </label>
                <Input
                  id="ceremonies_per_year"
                  type="number"
                  min="0"
                  value={formData.ceremonies_per_year}
                  onChange={(e) => setFormData({ ...formData, ceremonies_per_year: e.target.value })}
                  className="mt-1"
                />
              </div>

              <div>
                <label htmlFor="current_software" className="block text-sm font-medium text-gray-700">
                  Current Business Management Software
                </label>
                <Input
                  id="current_software"
                  type="text"
                  placeholder="e.g., Excel, Google Docs, etc."
                  value={formData.current_software}
                  onChange={(e) => setFormData({ ...formData, current_software: e.target.value })}
                  className="mt-1"
                />
              </div>

              <div>
                <label htmlFor="pain_points" className="block text-sm font-medium text-gray-700">
                  What are your biggest challenges in managing your celebrant business?
                </label>
                <textarea
                  id="pain_points"
                  rows={4}
                  value={formData.pain_points}
                  onChange={(e) => setFormData({ ...formData, pain_points: e.target.value })}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                />
              </div>
            </div>

            <div className="flex items-center justify-end space-x-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => router.push('/')}
                disabled={loading}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={loading}
                className="bg-primary hover:bg-primary-dark text-white"
              >
                {loading ? 'Submitting...' : 'Join Beta Program'}
              </Button>
            </div>
          </form>
        </Card>
      </div>
    </div>
  );
} 