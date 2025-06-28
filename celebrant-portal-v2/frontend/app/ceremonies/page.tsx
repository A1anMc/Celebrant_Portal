'use client';

import React, { useState } from 'react';
import DashboardLayout from '../../src/components/layout/DashboardLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../src/components/ui/Card';
import { Button } from '../../src/components/ui/Button';
import { Input } from '../../src/components/ui/Input';
import { 
  Calendar, 
  MapPin, 
  Clock, 
  Users, 
  Heart,
  Plus,
  Search,
  Filter,
  Eye,
  Edit,
  Trash2
} from 'lucide-react';

interface Ceremony {
  id: number;
  coupleName: string;
  date: string;
  time: string;
  venue: string;
  location: string;
  status: 'Confirmed' | 'Pending' | 'Completed' | 'Cancelled';
  type: 'Wedding' | 'Renewal' | 'Commitment';
  guests: number;
}

const mockCeremonies: Ceremony[] = [
  {
    id: 1,
    coupleName: "Emma & James Wilson",
    date: "2024-07-15",
    time: "2:00 PM",
    venue: "Royal Botanic Gardens",
    location: "Melbourne, VIC",
    status: "Confirmed",
    type: "Wedding",
    guests: 120
  },
  {
    id: 2,
    coupleName: "Sarah & Michael Chen",
    date: "2024-07-22",
    time: "11:00 AM",
    venue: "Brighton Beach",
    location: "Brighton, VIC",
    status: "Confirmed",
    type: "Wedding",
    guests: 80
  },
  {
    id: 3,
    coupleName: "Lisa & David Thompson",
    date: "2024-08-05",
    time: "4:00 PM",
    venue: "Yarra Valley Estate",
    location: "Yarra Valley, VIC",
    status: "Pending",
    type: "Wedding",
    guests: 150
  }
];

export default function CeremoniesPage() {
  const [ceremonies, setCeremonies] = useState<Ceremony[]>(mockCeremonies);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('All');

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Confirmed':
        return 'bg-success/10 text-success border-success/20';
      case 'Pending':
        return 'bg-warning/10 text-warning border-warning/20';
      case 'Completed':
        return 'bg-primary/10 text-primary border-primary/20';
      case 'Cancelled':
        return 'bg-destructive/10 text-destructive border-destructive/20';
      default:
        return 'bg-muted text-foreground/60 border-border';
    }
  };

  const filteredCeremonies = ceremonies.filter(ceremony => {
    const matchesSearch = ceremony.coupleName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         ceremony.venue.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'All' || ceremony.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <DashboardLayout>
      <div className="space-y-8 animate-fade-in">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div className="space-y-1">
            <h1 className="text-4xl font-serif font-bold text-primary-dark">Ceremonies</h1>
            <p className="text-lg text-foreground/70">Manage your upcoming and past ceremonies</p>
          </div>
          <Button 
            size="lg" 
            className="bg-primary hover:bg-primary-dark text-white shadow-soft hover:shadow-soft-lg transition-all duration-200"
          >
            <Plus className="mr-2 h-5 w-5" />
            New Ceremony
          </Button>
        </div>

        {/* Filters */}
        <Card className="shadow-soft">
          <CardContent className="p-6">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <Input
                  placeholder="Search ceremonies..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  leftIcon={<Search className="h-4 w-4" />}
                  className="w-full"
                />
              </div>
              <div className="flex gap-2">
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="px-4 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <option value="All">All Status</option>
                  <option value="Confirmed">Confirmed</option>
                  <option value="Pending">Pending</option>
                  <option value="Completed">Completed</option>
                  <option value="Cancelled">Cancelled</option>
                </select>
                <Button variant="outline" size="sm">
                  <Filter className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Ceremonies Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {filteredCeremonies.map((ceremony, index) => (
            <Card 
              key={ceremony.id} 
              className="shadow-soft hover:shadow-soft-lg transition-all duration-200 border-border/50 animate-slide-up"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <CardHeader className="pb-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-2">
                    <Heart className="h-5 w-5 text-primary" />
                    <CardTitle className="text-lg font-serif text-primary-dark">
                      {ceremony.coupleName}
                    </CardTitle>
                  </div>
                  <div className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(ceremony.status)}`}>
                    {ceremony.status}
                  </div>
                </div>
                <CardDescription className="text-sm text-foreground/60">
                  {ceremony.type} Ceremony
                </CardDescription>
              </CardHeader>
              
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center space-x-3 text-sm">
                    <Calendar className="h-4 w-4 text-primary" />
                    <span className="font-medium text-foreground">{ceremony.date}</span>
                  </div>
                  
                  <div className="flex items-center space-x-3 text-sm">
                    <Clock className="h-4 w-4 text-primary" />
                    <span className="text-foreground/70">{ceremony.time}</span>
                  </div>
                  
                  <div className="flex items-center space-x-3 text-sm">
                    <MapPin className="h-4 w-4 text-primary" />
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-foreground truncate">{ceremony.venue}</p>
                      <p className="text-foreground/60 text-xs">{ceremony.location}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3 text-sm">
                    <Users className="h-4 w-4 text-primary" />
                    <span className="text-foreground/70">{ceremony.guests} guests</span>
                  </div>
                </div>

                <div className="flex space-x-2 pt-4 border-t border-border/30">
                  <Button variant="outline" size="sm" className="flex-1">
                    <Eye className="h-4 w-4 mr-1" />
                    View
                  </Button>
                  <Button variant="outline" size="sm" className="flex-1">
                    <Edit className="h-4 w-4 mr-1" />
                    Edit
                  </Button>
                  <Button variant="outline" size="sm" className="text-destructive hover:text-destructive">
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Empty State */}
        {filteredCeremonies.length === 0 && (
          <Card className="shadow-soft">
            <CardContent className="p-12 text-center">
              <Heart className="h-16 w-16 text-primary/30 mx-auto mb-4" />
              <h3 className="text-xl font-serif font-semibold text-primary-dark mb-2">
                No ceremonies found
              </h3>
              <p className="text-foreground/60 mb-6">
                {searchTerm || statusFilter !== 'All' 
                  ? 'Try adjusting your search or filter criteria.'
                  : 'Start by creating your first ceremony.'}
              </p>
              <Button className="bg-primary hover:bg-primary-dark text-white">
                <Plus className="mr-2 h-4 w-4" />
                Create New Ceremony
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
} 