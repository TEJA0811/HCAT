import { Module } from '@nestjs/common';
import { UsersService } from './users.service';
import { UsersController } from './users.controller';
import { TypeOrmModule } from '@nestjs/typeorm';
import { User } from './entities/user.entity';
import { Project } from '../projects/entities/project.entity';
import { Team } from '../teams/entities/team.entity';
import { Manager } from '../managers/entities/manager.entity';

@Module({
  imports: [TypeOrmModule.forFeature([User,Project,Team,Manager])],
  controllers: [UsersController],
  providers: [UsersService],
  exports: [UsersService]
})
export class UsersModule {}
