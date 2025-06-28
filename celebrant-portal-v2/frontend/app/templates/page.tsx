'use client';

import DashboardLayout from '../../src/components/layout/DashboardLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../src/components/ui/Card';
import { Button } from '../../src/components/ui/Button';
import { FileText, Plus, Heart, Star, Clock, Users, BookOpen } from 'lucide-react';

export default function TemplatesPage() {
  const templateCategories = [
    {
      icon: Heart,
      title: "Wedding Ceremonies",
      description: "Traditional and modern wedding ceremony scripts",
      count: 12,
      color: "bg-primary/10 text-primary"
    },
    {
      icon: Star,
      title: "Vow Renewals", 
      description: "Romantic renewal ceremony templates",
      count: 6,
      color: "bg-accent/20 text-primary"
    },
    {
      icon: Users,
      title: "Commitment Ceremonies",
      description: "Personalized commitment ceremony scripts",
      count: 8,
      color: "bg-success/10 text-success"
    }
  ];

  return (
    <DashboardLayout>
      <div className="space-y-8 animate-fade-in">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div className="space-y-1">
            <h1 className="text-4xl font-serif font-bold text-primary-dark flex items-center">
              <BookOpen className="h-8 w-8 text-primary mr-3" />
              Ceremony Templates
            </h1>
            <p className="text-lg text-foreground/70">Create and manage your ceremony scripts and templates</p>
          </div>
          <Button 
            size="lg" 
            className="bg-primary hover:bg-primary-dark text-white shadow-soft hover:shadow-soft-lg transition-all duration-200"
          >
            <Plus className="mr-2 h-5 w-5" />
            New Template
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {templateCategories.map((category, index) => {
            const Icon = category.icon;
            return (
              <Card 
                key={category.title} 
                className="shadow-soft hover:shadow-soft-lg transition-all duration-200 border-border/50 animate-slide-up"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <CardHeader>
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-full ${category.color}`}>
                      <Icon className="h-5 w-5" />
                    </div>
                    <div>
                      <CardTitle className="text-lg font-serif text-primary-dark">{category.title}</CardTitle>
                      <CardDescription>{category.description}</CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <span className="text-2xl font-serif font-bold text-primary-dark">{category.count}</span>
                    <span className="text-sm text-foreground/60">templates</span>
                  </div>
                  <Button variant="outline" className="w-full mt-4">
                    <FileText className="mr-2 h-4 w-4" />
                    View Templates
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>

        <Card className="shadow-soft border-border/50">
          <CardHeader>
            <div className="flex items-center space-x-3">
              <div className="bg-warning/10 p-2 rounded-full">
                <Clock className="h-5 w-5 text-warning" />
              </div>
              <div>
                <CardTitle className="text-xl font-serif text-primary-dark">Coming Soon</CardTitle>
                <CardDescription>Advanced template management system</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-foreground/70 mb-4">
              The full template management system is being crafted with love. Soon you'll be able to:
            </p>
            <ul className="list-disc list-inside space-y-2 text-foreground/60">
              <li>Create custom ceremony scripts with drag-and-drop elements</li>
              <li>Personalize templates with couple-specific details</li>
              <li>Share and collaborate on ceremony scripts</li>
              <li>Access a library of professionally written templates</li>
              <li>Generate beautiful PDF ceremony scripts</li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
} 