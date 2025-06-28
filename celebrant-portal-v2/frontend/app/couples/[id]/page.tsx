'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import DashboardLayout from '../../../src/components/layout/DashboardLayout';
import { Button } from '../../../src/components/ui/Button';
import { Card } from '../../../src/components/ui/Card';
import { ArrowLeft, Edit, Trash2, User, Heart, Phone, Mail, MapPin, Calendar } from 'lucide-react';
import { couplesService } from '../../../src/services/couples';
import { Couple } from '../../../src/types';

export default function CoupleDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [couple, setCouple] = useState<Couple | null>(null);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);

  const coupleId = Array.isArray(params.id) ? params.id[0] : params.id;

  useEffect(() => {
    if (coupleId) {
      fetchCouple();
    }
  }, [coupleId]);

  const fetchCouple = async () => {
    try {
      setLoading(true);
      const coupleData = await couplesService.getCoupleById(parseInt(coupleId));
      setCouple(coupleData);
    } catch (error) {
      console.error('Error fetching couple:', error);
      alert('Failed to load couple details');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!couple) return;
    
    const confirmed = confirm(`Are you sure you want to delete ${couple.full_names}? This action cannot be undone.`);
    
    if (!confirmed) return;

    try {
      setDeleting(true);
      await couplesService.deleteCouple(couple.id);
      router.push('/couples?success=deleted');
    } catch (error) {
      console.error('Error deleting couple:', error);
      alert('Failed to delete couple. Please try again.');
    } finally {
      setDeleting(false);
    }
  };

  const getStatusColor = (status: string) => {
    const colors = {
      inquiry: 'bg-blue-100 text-blue-800',
      consultation: 'bg-yellow-100 text-yellow-800',
      booked: 'bg-green-100 text-green-800',
      confirmed: 'bg-purple-100 text-purple-800',
      completed: 'bg-gray-100 text-gray-800',
      cancelled: 'bg-red-100 text-red-800'
    };
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Not specified';
    return new Date(dateString).toLocaleDateString('en-AU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading couple details...</p>
        </div>
      </DashboardLayout>
    );
  }

  if (!couple) {
    return (
      <DashboardLayout>
        <div className="text-center py-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Couple Not Found</h2>
          <p className="text-gray-600 mb-6">The couple you're looking for doesn't exist or has been deleted.</p>
          <Link href="/couples">
            <Button>Back to Couples</Button>
          </Link>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="p-6">
        {/* Header */}
        <div className="flex justify-between items-start mb-6">
          <div className="flex items-center gap-4">
            <Link href="/couples">
              <Button variant="outline" size="sm">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Couples
              </Button>
            </Link>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {couple.full_names}
              </h1>
              <div className="flex items-center gap-2 mt-1">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(couple.status)}`}>
                  {couple.status.charAt(0).toUpperCase() + couple.status.slice(1)}
                </span>
                <span className="text-sm text-gray-500">
                  Added {formatDate(couple.created_at)}
                </span>
              </div>
            </div>
          </div>
          <div className="flex gap-2">
            <Button variant="outline">
              <Edit className="w-4 h-4 mr-2" />
              Edit
            </Button>
            <Button 
              variant="outline" 
              onClick={handleDelete}
              disabled={deleting}
              className="text-red-600 hover:text-red-700 border-red-200 hover:border-red-300"
            >
              {deleting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-red-600 mr-2"></div>
                  Deleting...
                </>
              ) : (
                <>
                  <Trash2 className="w-4 h-4 mr-2" />
                  Delete
                </>
              )}
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Partner 1 Details */}
          <Card className="p-6">
            <div className="flex items-center gap-2 mb-4">
              <User className="w-5 h-5 text-blue-600" />
              <h2 className="text-lg font-semibold text-gray-900">
                {couple.partner_1_first_name} {couple.partner_1_last_name}
              </h2>
            </div>
            <div className="space-y-3">
              {couple.partner_1_email && (
                <div className="flex items-center gap-2">
                  <Mail className="w-4 h-4 text-gray-400" />
                  <span className="text-sm text-gray-600">{couple.partner_1_email}</span>
                </div>
              )}
              {couple.partner_1_phone && (
                <div className="flex items-center gap-2">
                  <Phone className="w-4 h-4 text-gray-400" />
                  <span className="text-sm text-gray-600">{couple.partner_1_phone}</span>
                </div>
              )}
              {couple.partner_1_address && (
                <div className="flex items-start gap-2">
                  <MapPin className="w-4 h-4 text-gray-400 mt-0.5" />
                  <span className="text-sm text-gray-600">{couple.partner_1_address}</span>
                </div>
              )}
              {couple.partner_1_date_of_birth && (
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-gray-400" />
                  <span className="text-sm text-gray-600">Born: {formatDate(couple.partner_1_date_of_birth)}</span>
                </div>
              )}
            </div>
          </Card>

          {/* Partner 2 Details */}
          <Card className="p-6">
            <div className="flex items-center gap-2 mb-4">
              <User className="w-5 h-5 text-pink-600" />
              <h2 className="text-lg font-semibold text-gray-900">
                {couple.partner_2_first_name} {couple.partner_2_last_name}
              </h2>
            </div>
            <div className="space-y-3">
              {couple.partner_2_email && (
                <div className="flex items-center gap-2">
                  <Mail className="w-4 h-4 text-gray-400" />
                  <span className="text-sm text-gray-600">{couple.partner_2_email}</span>
                </div>
              )}
              {couple.partner_2_phone && (
                <div className="flex items-center gap-2">
                  <Phone className="w-4 h-4 text-gray-400" />
                  <span className="text-sm text-gray-600">{couple.partner_2_phone}</span>
                </div>
              )}
              {couple.partner_2_address && (
                <div className="flex items-start gap-2">
                  <MapPin className="w-4 h-4 text-gray-400 mt-0.5" />
                  <span className="text-sm text-gray-600">{couple.partner_2_address}</span>
                </div>
              )}
              {couple.partner_2_date_of_birth && (
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-gray-400" />
                  <span className="text-sm text-gray-600">Born: {formatDate(couple.partner_2_date_of_birth)}</span>
                </div>
              )}
            </div>
          </Card>

          {/* Additional Details */}
          <Card className="p-6 lg:col-span-2">
            <div className="space-y-4">
              {couple.notes && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Notes</h3>
                  <p className="text-sm text-gray-600 whitespace-pre-wrap">{couple.notes}</p>
                </div>
              )}
            </div>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
} 