'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from 'sonner';
import Link from 'next/link';
import { api } from '@/lib/api';
import { ThemeToggle } from '@/components/theme-toggle';
import { Wallet, UserPlus, Loader2 } from 'lucide-react';

interface Country {
  name: string;
  currencies: string[];
  currency_names: string[];
  primary_currency: string;
}

export default function SignupPage() {
  const router = useRouter();
  const { signup } = useAuth();
  const [loading, setLoading] = useState(false);
  const [countries, setCountries] = useState<Country[]>([]);
  const [loadingCountries, setLoadingCountries] = useState(true);
  const [step, setStep] = useState(1); // Step 1: First 4 fields, Step 2: Last 2 fields
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    company_name: '',
    currency: 'USD',
  });
  const [selectedCountry, setSelectedCountry] = useState('');

  useEffect(() => {
    const fetchCountries = async () => {
      try {
        const response = await api.countries.list();
        setCountries(response.data.data || []);
      } catch (error) {
        console.error('Failed to fetch countries:', error);
        toast.error('Failed to load countries');
      } finally {
        setLoadingCountries(false);
      }
    };

    fetchCountries();
  }, []);

  const handleCountryChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const countryName = e.target.value;
    setSelectedCountry(countryName);
    const country = countries.find(c => c.name === countryName);
    
    if (country) {
      setFormData({ 
        ...formData, 
        currency: country.primary_currency 
      });
    }
  };

  const handleNext = (e: React.FormEvent) => {
    e.preventDefault();
    // Validate first 4 fields
    if (!formData.company_name || !formData.name || !formData.email || !formData.password) {
      toast.error('Please fill in all fields');
      return;
    }
    if (formData.password.length < 8) {
      toast.error('Password must be at least 8 characters');
      return;
    }
    setStep(2);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedCountry) {
      toast.error('Please select your country');
      return;
    }

    setLoading(true);

    try {
      await signup(formData);
      toast.success('Account created successfully! 🎉');
      router.push('/dashboard');
    } catch (error: any) {
      toast.error(error.message || 'Signup failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4 py-8 relative">
      {/* Theme toggle */}
      <div className="absolute top-4 right-4 z-10">
        <ThemeToggle />
      </div>

      {/* Centered Signup Card */}
      <div className="w-full max-w-md">
        {/* Logo Header */}
        <div className="flex justify-center mb-8">
          <div className="flex items-center space-x-3">
            <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-lg">
              <Wallet className="h-7 w-7" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Expense Tracker</h1>
              <p className="text-sm text-muted-foreground">Create your account</p>
            </div>
          </div>
        </div>

        {/* Signup Form Card */}
        <Card className="shadow-lg">
          <CardHeader className="space-y-1 text-center">
            <CardTitle className="text-2xl font-bold">Get Started</CardTitle>
            <CardDescription>
              {step === 1 ? 'Step 1 of 2: Basic Information' : 'Step 2 of 2: Location & Currency'}
            </CardDescription>
            {/* Progress Indicator */}
            <div className="flex gap-2 justify-center mt-4">
              <div className={`h-2 w-16 rounded-full ${step === 1 ? 'bg-primary' : 'bg-primary/50'}`} />
              <div className={`h-2 w-16 rounded-full ${step === 2 ? 'bg-primary' : 'bg-muted'}`} />
            </div>
          </CardHeader>

          {/* Step 1: First 4 Fields */}
          {step === 1 && (
            <form onSubmit={handleNext}>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="company_name">Company Name</Label>
                  <Input
                    id="company_name"
                    type="text"
                    placeholder="Acme Corp"
                    value={formData.company_name}
                    onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                    required
                    className="h-11"
                    autoComplete="organization"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="name">Your Name</Label>
                  <Input
                    id="name"
                    type="text"
                    placeholder="John Doe"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                    className="h-11"
                    autoComplete="name"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="you@example.com"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    required
                    className="h-11"
                    autoComplete="email"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <Input
                    id="password"
                    type="password"
                    placeholder="••••••••"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    required
                    minLength={8}
                    className="h-11"
                    autoComplete="new-password"
                  />
                  <p className="text-xs text-muted-foreground">Must be at least 8 characters</p>
                </div>
              </CardContent>

              <CardFooter className="flex flex-col space-y-4">
                <Button type="submit" className="w-full h-11">
                  Continue
                </Button>
                <p className="text-sm text-center text-muted-foreground">
                  Already have an account?{' '}
                  <Link href="/login" className="text-primary hover:underline font-medium">
                    Sign in
                  </Link>
                </p>
              </CardFooter>
            </form>
          )}

          {/* Step 2: Last 2 Fields */}
          {step === 2 && (
            <form onSubmit={handleSubmit}>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="country">Country</Label>
                  <select
                    id="country"
                    value={selectedCountry}
                    onChange={handleCountryChange}
                    disabled={loading || loadingCountries}
                    className="flex h-11 w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 [&>option]:bg-background [&>option]:text-foreground"
                    required
                  >
                    <option value="" className="bg-background text-foreground">Select your country</option>
                    {countries.map((country) => (
                      <option key={country.name} value={country.name} className="bg-background text-foreground">
                        {country.name}
                      </option>
                    ))}
                  </select>
                  <p className="text-xs text-muted-foreground">
                    Your currency will be set based on your country
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="currency">Company Currency</Label>
                  <Input
                    id="currency"
                    type="text"
                    value={formData.currency}
                    disabled
                    className="h-11 bg-muted"
                  />
                  <p className="text-xs text-muted-foreground">
                    Auto-selected: {formData.currency}
                  </p>
                </div>
              </CardContent>

              <CardFooter className="flex flex-col space-y-4">
                <div className="flex gap-3 w-full">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setStep(1)}
                    className="flex-1 h-11"
                    disabled={loading}
                  >
                    Back
                  </Button>
                  <Button
                    type="submit"
                    className="flex-1 h-11"
                    disabled={loading || loadingCountries}
                  >
                    {loading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Creating...
                      </>
                    ) : (
                      <>
                        <UserPlus className="mr-2 h-4 w-4" />
                        Create Account
                      </>
                    )}
                  </Button>
                </div>
                <p className="text-sm text-center text-muted-foreground">
                  Already have an account?{' '}
                  <Link href="/login" className="text-primary hover:underline font-medium">
                    Sign in
                  </Link>
                </p>
              </CardFooter>
            </form>
          )}
        </Card>
      </div>
    </div>
  );
}
