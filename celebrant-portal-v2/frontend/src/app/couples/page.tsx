'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Plus, Search, Users, Mail, Phone, Calendar, Filter } from 'lucide-react';
import { couplesService } from '@/services/couples';

interface Couple {
  id: number;
  partner_1_first_name: string;
  partner_1_last_name: string;
  partner_2_first_name: string;
  partner_2_last_name: string;
  status: string;
  primary_email?: string;
  primary_phone?: string;
  full_names?: string;
  created_at: string;
}

interface CouplesResponse {
  couples: Couple[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

export default function CouplesPage() {
  const [couples, setCouples] = useState<Couple[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);

  const statusOptions = [
    { value: '', label: 'All Statuses' },
    { value: 'inquiry', label: 'Inquiry' },
    { value: 'consultation', label: 'Consultation' },
    { value: 'booked', label: 'Booked' },
    { value: 'confirmed', label: 'Confirmed' },
    { value: 'completed', label: 'Completed' },
    { value: 'cancelled', label: 'Cancelled' }
  ];

  const fetchCouples = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (searchQuery) params.append('search', searchQuery);
      if (statusFilter) params.append('status', statusFilter);
      params.append('page', currentPage.toString());
      params.append('per_page', '20');

      const response: CouplesResponse = await couplesService.getCouples(params.toString());
      setCouples(response.couples);
      setTotal(response.total);
      setTotalPages(response.pages);
    } catch (error) {
      console.error('Error fetching couples:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCouples();
  }, [currentPage, searchQuery, statusFilter]);

  const handleSearch = () => {
    setCurrentPage(1);
    fetchCouples();
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

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-AU', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <DashboardLayout>
      <div className="p-6">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Couples Management</h1>
            <p className="text-gray-600 mt-1">
              {total} couple{total !== 1 ? 's' : ''} total
            </p>
          </div>
          <Link href="/couples/new">
            <Button className="bg-blue-600 hover:bg-blue-700">
              <Plus className="w-4 h-4 mr-2" />
              Add New Couple
            </Button>
          </Link>
        </div>

        {/* Search and Filters */}
        <Card className="p-4 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input
                  placeholder="Search by name or email..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="flex gap-2">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              >
                {statusOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              <Button onClick={handleSearch} variant="outline">
                <Filter className="w-4 h-4 mr-2" />
                Filter
              </Button>
            </div>
          </div>
        </Card>

        {/* Couples List */}
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading couples...</p>
          </div>
        ) : couples.length === 0 ? (
          <Card className="p-12 text-center">
            <Users className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No couples found</h3>
            <p className="text-gray-600 mb-4">
              {searchQuery || statusFilter ? 'Try adjusting your search or filters.' : "You haven't added any couples yet."}
            </p>
            <Link href="/couples/new">
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Add Your First Couple
              </Button>
            </Link>
          </Card>
        ) : (
          <div className="space-y-4">
            {couples.map((couple) => (
              <Card key={couple.id} className="p-6 hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-4">
                      <div>
                        <h3 className="text-lg font-medium text-gray-900">
                          {couple.full_names || `${couple.partner_1_first_name} ${couple.partner_1_last_name} & ${couple.partner_2_first_name} ${couple.partner_2_last_name}`}
                        </h3>
                        <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
                          {couple.primary_email && (
                            <div className="flex items-center gap-1">
                              <Mail className="w-4 h-4" />
                              {couple.primary_email}
                            </div>
                          )}
                          {couple.primary_phone && (
                            <div className="flex items-center gap-1">
                              <Phone className="w-4 h-4" />
                              {couple.primary_phone}
                            </div>
                          )}
                          <div className="flex items-center gap-1">
                            <Calendar className="w-4 h-4" />
                            Added {formatDate(couple.created_at)}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(couple.status)}`}>
                      {couple.status.charAt(0).toUpperCase() + couple.status.slice(1)}
                    </span>
                    <Link href={`/couples/${couple.id}`}>
                      <Button variant="outline" size="sm">
                        View Details
                      </Button>
                    </Link>
                  </div>
                </div>
              </Card>
            ))}

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex justify-center items-center gap-2 mt-6">
                <Button
                  variant="outline"
                  onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                  disabled={currentPage === 1}
                >
                  Previous
                </Button>
                <span className="px-4 py-2 text-sm text-gray-600">
                  Page {currentPage} of {totalPages}
                </span>
                <Button
                  variant="outline"
                  onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                  disabled={currentPage === totalPages}
                >
                  Next
                </Button>
              </div>
            )}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
} 