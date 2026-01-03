import { ConflictException, Injectable } from '@nestjs/common';
import { CreateUserDto } from './dto/create-user.dto';
import { UpdateUserDto } from './dto/update-user.dto';
import { User } from './entities/user.entity';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Team } from '../teams/entities/team.entity';
import { Manager } from '../managers/entities/manager.entity';

@Injectable()
export class UsersService {
  constructor(
    @InjectRepository(User)
    private readonly userRepository: Repository<User>,
        @InjectRepository(Team)
    private readonly teamRepository: Repository<Team>,
        @InjectRepository(Manager)
    private readonly managerRepository: Repository<Manager>,
  ) {}

  async create(createUserDto: CreateUserDto) {
  // Check if manager exists
  const manager = await this.managerRepository.findOne({
    where: { id: createUserDto.reports_to },
  });

  if (!manager) {
    throw new ConflictException('Manager not found');
  }

  //  Check if team exists and belongs to this manager
  const team = await this.teamRepository.findOne({
    where: { id: createUserDto.team_id, manager: { id: createUserDto.reports_to } },
    relations: ['manager'],
  });

  

  if (!team) {
     throw new ConflictException(
      'Team does not belong to this Manager');
  }
    const user = this.userRepository.create(createUserDto);
    return await this.userRepository.save(user);
  }

  async findAll(): Promise<User[]> {
    return await this.userRepository.find(
      { relations: ['team', 'project', 'manager'] }
    );
  }


  // Get user with team and projects
async findone(id: number): Promise<User | null> {
  return await this.userRepository.findOne({
    where: { id },
    relations: ['team', 'project', 'manager'],
  });
}

  async findBy(query: object) {
    return await User.findOne(query);
  }

  async update(id: number, updateUserDto: UpdateUserDto) {
    await User.update({ id }, updateUserDto);
    return await User.findOneBy({ id });
  }

  async remove(id: number) {
    await User.delete({ id });
    return { deleted: true };
  }
}
