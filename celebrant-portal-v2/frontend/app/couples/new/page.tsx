'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import DashboardLayout from '../../../src/components/layout/DashboardLayout';
import { Button } from '../../../src/components/ui/Button';
import { Card } from '../../../src/components/ui/Card';
import { Input } from '../../../src/components/ui/Input';
import { ArrowLeft, Save, User, Heart, Phone, Mail, MapPin, Calendar } from 'lucide-react';
import { couplesService } from '../../../src/services/couples';
import Link from 'next/link';

export default function NewCouplePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    // Partner 1
    partner_1_first_name: '',
    partner_1_last_name: '',
    partner_1_phone: '',
    partner_1_email: '',
    partner_1_address: '',
    partner_1_date_of_birth: '',
    
    // Partner 2
    partner_2_first_name: '',
    partner_2_last_name: '',
    partner_2_phone: '',
    partner_2_email: '',
    partner_2_address: '',
    partner_2_date_of_birth: '',
    
    // Relationship Information
    relationship_start_date: '',
    previous_marriages: '',
    
    // Contact & Status
    primary_contact: 'partner_1',
    preferred_contact_method: 'email',
    status: 'inquiry',
    notes: '',
    internal_notes: '',
    referral_source: '',
    marketing_consent: 'not_specified'
  });

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Convert empty strings to null for optional fields
      const submitData = Object.entries(formData).reduce((acc, [key, value]) => {
        acc[key] = value === '' ? null : value;
        return acc;
      }, {} as any);

      await couplesService.createCouple(submitData);
      
      // Redirect to couples list with success message
      router.push('/couples?success=created');
    } catch (error) {
      console.error('Error creating couple:', error);
      alert('Failed to create couple. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center gap-4 mb-6">
          <Link href="/couples">
            <Button variant="outline" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Couples
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Add New Couple</h1>
            <p className="text-gray-600 mt-1">Enter the couple's details to get started</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Partner 1 Details */}
          <Card className="p-6">
            <div className="flex items-center gap-2 mb-4">
              <User className="w-5 h-5 text-blue-600" />
              <h2 className="text-lg font-semibold text-gray-900">Partner 1 Details</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  First Name *
                </label>
                <Input
                  value={formData.partner_1_first_name}
                  onChange={(e) => handleInputChange('partner_1_first_name', e.target.value)}
                  required
                  placeholder="Enter first name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Last Name *
                </label>
                <Input
                  value={formData.partner_1_last_name}
                  onChange={(e) => handleInputChange('partner_1_last_name', e.target.value)}
                  required
                  placeholder="Enter last name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    type="email"
                    value={formData.partner_1_email}
                    onChange={(e) => handleInputChange('partner_1_email', e.target.value)}
                    placeholder="Enter email address"
                    className="pl-10"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Phone
                </label>
                <div className="relative">
                  <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    type="tel"
                    value={formData.partner_1_phone}
                    onChange={(e) => handleInputChange('partner_1_phone', e.target.value)}
                    placeholder="Enter phone number"
                    className="pl-10"
                  />
                </div>
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Address
                </label>
                <div className="relative">
                  <MapPin className="absolute left-3 top-3 text-gray-400 w-4 h-4" />
                  <Input
                    value={formData.partner_1_address}
                    onChange={(e) => handleInputChange('partner_1_address', e.target.value)}
                    placeholder="Enter full address"
                    className="pl-10"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Date of Birth
                </label>
                <div className="relative">
                  <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    type="date"
                    value={formData.partner_1_date_of_birth}
                    onChange={(e) => handleInputChange('partner_1_date_of_birth', e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
            </div>
          </Card>

          {/* Partner 2 Details */}
          <Card className="p-6">
            <div className="flex items-center gap-2 mb-4">
              <User className="w-5 h-5 text-pink-600" />
              <h2 className="text-lg font-semibold text-gray-900">Partner 2 Details</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  First Name *
                </label>
                <Input
                  value={formData.partner_2_first_name}
                  onChange={(e) => handleInputChange('partner_2_first_name', e.target.value)}
                  required
                  placeholder="Enter first name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Last Name *
                </label>
                <Input
                  value={formData.partner_2_last_name}
                  onChange={(e) => handleInputChange('partner_2_last_name', e.target.value)}
                  required
                  placeholder="Enter last name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    type="email"
                    value={formData.partner_2_email}
                    onChange={(e) => handleInputChange('partner_2_email', e.target.value)}
                    placeholder="Enter email address"
                    className="pl-10"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Phone
                </label>
                <div className="relative">
                  <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    type="tel"
                    value={formData.partner_2_phone}
                    onChange={(e) => handleInputChange('partner_2_phone', e.target.value)}
                    placeholder="Enter phone number"
                    className="pl-10"
                  />
                </div>
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Address
                </label>
                <div className="relative">
                  <MapPin className="absolute left-3 top-3 text-gray-400 w-4 h-4" />
                  <Input
                    value={formData.partner_2_address}
                    onChange={(e) => handleInputChange('partner_2_address', e.target.value)}
                    placeholder="Enter full address"
                    className="pl-10"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Date of Birth
                </label>
                <div className="relative">
                  <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    type="date"
                    value={formData.partner_2_date_of_birth}
                    onChange={(e) => handleInputChange('partner_2_date_of_birth', e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
            </div>
          </Card>

          {/* Relationship Information */}
          <Card className="p-6">
            <div className="flex items-center gap-2 mb-4">
              <Heart className="w-5 h-5 text-red-600" />
              <h2 className="text-lg font-semibold text-gray-900">Relationship Information</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Relationship Start Date
                </label>
                <Input
                  type="date"
                  value={formData.relationship_start_date}
                  onChange={(e) => handleInputChange('relationship_start_date', e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Previous Marriages
                </label>
                <select
                  value={formData.previous_marriages}
                  onChange={(e) => handleInputChange('previous_marriages', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Select option</option>
                  <option value="none">None</option>
                  <option value="partner_1">Partner 1 only</option>
                  <option value="partner_2">Partner 2 only</option>
                  <option value="both">Both partners</option>
                </select>
              </div>
            </div>
          </Card>

          {/* Contact & Status */}
          <Card className="p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Contact & Status Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Primary Contact
                </label>
                <select
                  value={formData.primary_contact}
                  onChange={(e) => handleInputChange('primary_contact', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="partner_1">Partner 1</option>
                  <option value="partner_2">Partner 2</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Preferred Contact Method
                </label>
                <select
                  value={formData.preferred_contact_method}
                  onChange={(e) => handleInputChange('preferred_contact_method', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="email">Email</option>
                  <option value="phone">Phone</option>
                  <option value="text">Text Message</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Status
                </label>
                <select
                  value={formData.status}
                  onChange={(e) => handleInputChange('status', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="inquiry">Inquiry</option>
                  <option value="consultation">Consultation</option>
                  <option value="booked">Booked</option>
                  <option value="confirmed">Confirmed</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Referral Source
                </label>
                <Input
                  value={formData.referral_source}
                  onChange={(e) => handleInputChange('referral_source', e.target.value)}
                  placeholder="How did they find you?"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Notes
                </label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => handleInputChange('notes', e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Add any notes about the couple or their requirements..."
                />
              </div>
            </div>
          </Card>

          {/* Form Actions */}
          <div className="flex justify-end gap-4">
            <Link href="/couples">
              <Button type="button" variant="outline">
                Cancel
              </Button>
            </Link>
            <Button type="submit" disabled={loading} className="bg-blue-600 hover:bg-blue-700">
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Creating...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4 mr-2" />
                  Create Couple
                </>
              )}
            </Button>
          </div>
        </form>
      </div>
    </DashboardLayout>
  );
} 