'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import DashboardLayout from '../../src/components/layout/DashboardLayout';
import { Button } from '../../src/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../src/components/ui/Card';
import { Input } from '../../src/components/ui/Input';
import { Plus, Search, Users, Mail, Phone, Calendar, Filter, Heart, MapPin, Clock } from 'lucide-react';
import { couplesService } from '../../src/services/couples';
import { Couple, CoupleSearchParams } from '../../src/types';

interface CouplesResponse {
  couples: Couple[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

export default function CouplesPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [couples, setCouples] = useState<Couple[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState(searchParams.get('search') || '');
  const [currentPage, setCurrentPage] = useState(parseInt(searchParams.get('page') || '1'));
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(0);

  const statusOptions = [
    { value: '', label: 'All Statuses' },
    { value: 'inquiry', label: 'Inquiry' },
    { value: 'consultation', label: 'Consultation' },
    { value: 'booked', label: 'Booked' },
    { value: 'confirmed', label: 'Confirmed' },
    { value: 'completed', label: 'Completed' },
    { value: 'cancelled', label: 'Cancelled' }
  ];

  useEffect(() => {
    fetchCouples();
  }, [currentPage, searchTerm]);

  const fetchCouples = async () => {
    try {
      setLoading(true);
      const searchParams: CoupleSearchParams = {
        page: currentPage,
        per_page: 20
      };

      if (searchTerm) {
        searchParams.search = searchTerm;
      }

      const response = await couplesService.getCouples(searchParams);
      setCouples(response.couples);
      setTotal(response.total);
      setTotalPages(response.pages);
    } catch (error) {
      console.error('Error fetching couples:', error);
      alert('Failed to load couples');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage(1);
    const params = new URLSearchParams();
    if (searchTerm) params.append('search', searchTerm);
    params.append('page', '1');
    router.push(`/couples?${params.toString()}`);
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    const params = new URLSearchParams();
    if (searchTerm) params.append('search', searchTerm);
    params.append('page', page.toString());
    router.push(`/couples?${params.toString()}`);
  };

  const getStatusColor = (status: string) => {
    const colors = {
      inquiry: 'bg-blue-100 text-blue-800 border-blue-200',
      consultation: 'bg-amber-100 text-amber-800 border-amber-200',
      booked: 'bg-emerald-100 text-emerald-800 border-emerald-200',
      confirmed: 'bg-purple-100 text-purple-800 border-purple-200',
      completed: 'bg-slate-100 text-slate-800 border-slate-200',
      cancelled: 'bg-red-100 text-red-800 border-red-200'
    };
    return colors[status as keyof typeof colors] || 'bg-muted text-foreground border-border';
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
      <div className="space-y-8 animate-fade-in">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div className="space-y-1">
            <h1 className="text-4xl font-serif font-bold text-primary-dark flex items-center">
              <Heart className="h-8 w-8 text-primary mr-3" />
              Couples Management
            </h1>
            <p className="text-lg text-foreground/70">
              {total} couple{total !== 1 ? 's' : ''} in your beautiful collection
            </p>
          </div>
          <Link href="/couples/new">
            <Button 
              size="lg" 
              className="bg-primary hover:bg-primary-dark text-white shadow-soft hover:shadow-soft-lg transition-all duration-200"
            >
              <Plus className="w-5 h-5 mr-2" />
              Add New Couple
            </Button>
          </Link>
        </div>

        {/* Search and Filters */}
        <Card className="shadow-soft border-border/50">
          <CardContent className="p-6">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-foreground/40 w-5 h-5" />
                  <Input
                    placeholder="Search by name, email, or venue..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSearch(e)}
                    className="pl-12 h-12 text-base border-border/50 focus:border-primary/50 focus:ring-primary/20"
                  />
                </div>
              </div>
              <div className="flex gap-3">
                <select
                  value={searchParams.get('status') || ''}
                  onChange={(e) => {
                    const params = new URLSearchParams(searchParams.toString());
                    params.set('status', e.target.value);
                    router.push(`/couples?${params.toString()}`);
                  }}
                  className="px-4 py-3 border border-border/50 rounded-lg focus:ring-primary/20 focus:border-primary/50 bg-card text-foreground h-12"
                >
                  {statusOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
                <Button onClick={handleSearch} variant="outline" size="lg" className="h-12">
                  <Filter className="w-4 h-4 mr-2" />
                  Filter
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Couples List */}
        {loading ? (
          <div className="text-center py-16 animate-fade-in">
            <div className="bg-primary/10 rounded-full p-4 w-16 h-16 mx-auto mb-6 flex items-center justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
            <p className="text-lg text-foreground/60 font-medium">Loading your couples...</p>
          </div>
        ) : couples.length === 0 ? (
          <Card className="shadow-soft border-border/50">
            <CardContent className="p-16 text-center">
              <div className="bg-muted/30 rounded-full p-6 w-24 h-24 mx-auto mb-6 flex items-center justify-center">
                <Users className="w-12 h-12 text-foreground/40" />
              </div>
              <h3 className="text-2xl font-serif font-semibold text-primary-dark mb-3">No couples found</h3>
              <p className="text-foreground/60 mb-6 max-w-md mx-auto">
                {searchTerm ? 'Try adjusting your search or filters to find what you\'re looking for.' : "You haven't added any couples yet. Start building your beautiful collection of love stories."}
              </p>
              <Link href="/couples/new">
                <Button size="lg" className="bg-primary hover:bg-primary-dark">
                  <Plus className="w-5 h-5 mr-2" />
                  Add Your First Couple
                </Button>
              </Link>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-6">
            {couples.map((couple, index) => (
              <Card 
                key={couple.id} 
                className="shadow-soft hover:shadow-soft-lg transition-all duration-200 border-border/50 hover:border-primary/30 animate-slide-up"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-start gap-4">
                        <div className="bg-primary/10 rounded-full p-3 flex-shrink-0">
                          <Heart className="w-6 h-6 text-primary" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <h3 className="text-xl font-serif font-semibold text-primary-dark mb-2">
                            {couple.full_names || `${couple.partner_1_first_name} ${couple.partner_1_last_name} & ${couple.partner_2_first_name} ${couple.partner_2_last_name}`}
                          </h3>
                          
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                            {couple.primary_email && (
                              <div className="flex items-center gap-2 text-foreground/70">
                                <Mail className="w-4 h-4 text-primary/70" />
                                <span className="truncate">{couple.primary_email}</span>
                              </div>
                            )}
                            {couple.primary_phone && (
                              <div className="flex items-center gap-2 text-foreground/70">
                                <Phone className="w-4 h-4 text-primary/70" />
                                <span>{couple.primary_phone}</span>
                              </div>
                            )}
                            <div className="flex items-center gap-2 text-foreground/70">
                              <Calendar className="w-4 h-4 text-primary/70" />
                              <span>Status: {couple.status}</span>
                            </div>
                          </div>

                          {couple.notes && (
                            <div className="mt-3 p-3 bg-muted/30 rounded-lg">
                              <p className="text-sm text-foreground/70 line-clamp-2">{couple.notes}</p>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex flex-col items-end gap-3 ml-4">
                      <div className={`inline-flex items-center px-3 py-1.5 rounded-full text-xs font-medium border ${getStatusColor(couple.status)}`}>
                        {couple.status}
                      </div>
                      
                      <div className="flex gap-2">
                        <Link href={`/couples/${couple.id}`}>
                          <Button variant="outline" size="sm" className="hover:bg-primary/5">
                            View Details
                          </Button>
                        </Link>
                      </div>
                      
                      {couple.created_at && (
                        <div className="flex items-center gap-1 text-xs text-foreground/50">
                          <Clock className="w-3 h-3" />
                          <span>Added {formatDate(couple.created_at)}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <Card className="shadow-soft border-border/50">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="text-sm text-foreground/60">
                  Showing {((currentPage - 1) * 20) + 1} to {Math.min(currentPage * 20, total)} of {total} couples
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                  >
                    Previous
                  </Button>
                  
                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    const page = Math.max(1, Math.min(totalPages - 4, currentPage - 2)) + i;
                    return (
                      <Button
                        key={page}
                        variant={currentPage === page ? "default" : "outline"}
                        size="sm"
                        onClick={() => handlePageChange(page)}
                        className={currentPage === page ? "bg-primary text-white" : ""}
                      >
                        {page}
                      </Button>
                    );
                  })}
                  
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={currentPage === totalPages}
                  >
                    Next
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
} 